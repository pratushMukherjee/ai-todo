import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Calendar, dateFnsLocalizer, Views } from 'react-big-calendar';
import withDragAndDrop from 'react-big-calendar/lib/addons/dragAndDrop';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import enUS from 'date-fns/locale/en-US';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import 'react-big-calendar/lib/addons/dragAndDrop/styles.css';
import { getCalendarEvents, createCalendarEvent, updateCalendarEvent, deleteCalendarEvent } from '../api/agent';
import { deleteTask, patchTask } from '../api/tasks';
import { ControlledMenu, MenuItem, useMenuState } from '@szhsin/react-menu';
import '@szhsin/react-menu/dist/index.css';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { FaEdit, FaTrash, FaCopy, FaStar, FaRegStar, FaPalette, FaCalendarPlus, FaExternalLinkAlt, FaClone, FaFileExport } from 'react-icons/fa';
import { CopyToClipboard } from 'copy-to-clipboard';
import { ICS } from 'ics';

const DnDCalendar = withDragAndDrop(Calendar);

const locales = {
  'en-US': enUS,
};
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

// Google Calendar colorId <-> hex mapping
const COLOR_ID_TO_HEX = {
  '1': '#a4bdfc',
  '2': '#7ae7bf',
  '3': '#dbadff',
  '4': '#ff887c',
  '5': '#fbd75b',
  '6': '#ffb878',
  '7': '#46d6db',
  '8': '#e1e1e1',
  '9': '#5484ed',
  '10': '#51b749',
  '11': '#dc2127',
  // Add more as needed
  '99': '#3174ad', // fallback/default
};
const HEX_TO_COLOR_ID = Object.fromEntries(Object.entries(COLOR_ID_TO_HEX).map(([id, hex]) => [hex.toLowerCase(), id]));

const colorOptions = Object.values(COLOR_ID_TO_HEX);

function CalendarPanel() {
  const [events, setEvents] = useState([]);
  const [view, setView] = useState(Views.MONTH);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    start: '',
    end: '',
    color: '#3174ad',
  });
  const [editEvent, setEditEvent] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [contextEvent, setContextEvent] = useState(null);
  const calendarRef = useRef();

  // Fetch events from backend
  const fetchEvents = useCallback(async () => {
    try {
      const apiEvents = await getCalendarEvents();
      // Convert Google events to react-big-calendar format
      const mapped = apiEvents.map(ev => {
        let colorHex = COLOR_ID_TO_HEX[ev.colorId] || '#3174ad';
        return {
          id: ev.id,
          title: ev.summary || 'No Title',
          start: new Date(ev.start?.dateTime || ev.start?.date),
          end: new Date(ev.end?.dateTime || ev.end?.date),
          allDay: !!ev.start?.date,
          color: colorHex,
          colorId: ev.colorId || '99',
          important: ev.important || false,
          meetingLink: ev.meetingLink || null,
          taskId: ev.taskId || null,
        };
      });
      setEvents(mapped);
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
    // Add polling for real-time updates
    const interval = setInterval(() => {
      fetchEvents();
    }, 5000); // 5 seconds
    return () => clearInterval(interval);
  }, [fetchEvents]);

  // Handle event creation
  const handleSelectSlot = ({ start, end }) => {
    setFormData({ title: '', start, end, color: '#3174ad' });
    setShowForm(true);
  };

  const handleFormChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFormSubmit = async e => {
    e.preventDefault();
    // Map color hex to colorId
    const colorId = HEX_TO_COLOR_ID[formData.color.toLowerCase()] || '99';
    const event = {
      summary: formData.title,
      start: { dateTime: new Date(formData.start).toISOString() },
      end: { dateTime: new Date(formData.end).toISOString() },
      colorId,
    };
    try {
      await createCalendarEvent(event);
      setShowForm(false);
      fetchEvents();
    } catch (err) {
      alert('Failed to create event');
    }
  };

  // Context menu logic
  const [menuProps, toggleMenu] = useMenuState({ transition: true });
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
  const handleEventContextMenu = (event, e) => {
    e.preventDefault();
    setContextEvent(event);
    setMenuPosition({ x: e.clientX, y: e.clientY });
    toggleMenu.open();
  };
  const closeMenu = () => toggleMenu.close();

  // Edit modal logic
  const openEditModal = () => {
    setEditEvent(contextEvent);
    setShowEditModal(true);
  };
  const closeEditModal = () => {
    setShowEditModal(false);
    setEditEvent(null);
  };
  const handleEditChange = e => {
    setEditEvent({ ...editEvent, [e.target.name]: e.target.value });
  };
  const handleEditSubmit = async e => {
    e.preventDefault();
    // Map color hex to colorId
    const colorId = HEX_TO_COLOR_ID[editEvent.color.toLowerCase()] || '99';
    try {
      await updateCalendarEvent(editEvent.id, {
        summary: editEvent.title,
        start: { dateTime: new Date(editEvent.start).toISOString() },
        end: { dateTime: new Date(editEvent.end).toISOString() },
        colorId,
      });
      fetchEvents();
      closeEditModal();
    } catch (err) {
      alert('Failed to update event');
    }
  };
  const handleDelete = async () => {
    if (!contextEvent) return;
    const confirmDelete = window.confirm('Delete this calendar event' + (contextEvent.taskId ? ' and its linked task?' : '?'));
    if (!confirmDelete) return;
    try {
      await deleteCalendarEvent(contextEvent.id);
      if (contextEvent.taskId) {
        await deleteTask(contextEvent.taskId);
      }
      fetchEvents();
      setContextEvent(null);
    } catch (err) {
      alert('Failed to delete event or task');
    }
  };

  // Add 'important' property to events
  const handleDuplicate = async () => {
    if (!contextEvent) return;
    const newEvent = {
      summary: contextEvent.title + ' (Copy)',
      start: { dateTime: new Date(contextEvent.start).toISOString() },
      end: { dateTime: new Date(contextEvent.end).toISOString() },
      colorId: contextEvent.colorId,
    };
    try {
      await createCalendarEvent(newEvent);
      fetchEvents();
    } catch (err) {
      alert('Failed to duplicate event');
    }
  };
  const handleMarkImportant = async () => {
    if (!contextEvent) return;
    // Toggle important property
    const updated = { ...contextEvent, important: !contextEvent.important };
    setEvents(events.map(ev => ev.id === updated.id ? updated : ev));
    // Optionally persist to backend if needed
    closeMenu();
  };
  const handleCopyDetails = () => {
    if (!contextEvent) return;
    const details = `Event: ${contextEvent.title}\nStart: ${contextEvent.start}\nEnd: ${contextEvent.end}`;
    navigator.clipboard.writeText(details);
    closeMenu();
  };
  const handleExportICS = () => {
    if (!contextEvent) return;
    const ics = require('ics');
    const event = {
      start: [
        contextEvent.start.getFullYear(),
        contextEvent.start.getMonth() + 1,
        contextEvent.start.getDate(),
        contextEvent.start.getHours(),
        contextEvent.start.getMinutes()
      ],
      end: [
        contextEvent.end.getFullYear(),
        contextEvent.end.getMonth() + 1,
        contextEvent.end.getDate(),
        contextEvent.end.getHours(),
        contextEvent.end.getMinutes()
      ],
      title: contextEvent.title,
      description: '',
      location: '',
    };
    ics.createEvent(event, (error, value) => {
      if (error) { alert('Failed to export .ics'); return; }
      const blob = new Blob([value], { type: 'text/calendar' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${contextEvent.title}.ics`;
      a.click();
      URL.revokeObjectURL(url);
    });
    closeMenu();
  };
  const handleJoinMeeting = () => {
    if (!contextEvent || !contextEvent.meetingLink) return;
    window.open(contextEvent.meetingLink, '_blank');
    closeMenu();
  };
  const handleColorChange = async (color) => {
    if (!contextEvent) return;
    const colorId = HEX_TO_COLOR_ID[color.toLowerCase()] || '99';
    try {
      await updateCalendarEvent(contextEvent.id, {
        summary: contextEvent.title,
        start: { dateTime: new Date(contextEvent.start).toISOString() },
        end: { dateTime: new Date(contextEvent.end).toISOString() },
        colorId,
      });
      fetchEvents();
      closeMenu();
    } catch (err) {
      alert('Failed to change color');
    }
  };

  // Drag and drop handlers
  const moveEvent = async ({ event, start, end, isAllDay: droppedOnAllDaySlot }) => {
    try {
      await updateCalendarEvent(event.id, {
        summary: event.title,
        start: { dateTime: new Date(start).toISOString() },
        end: { dateTime: new Date(end).toISOString() },
        colorId: event.colorId,
      });
      if (event.taskId) {
        await patchTask(event.taskId, {
          start: new Date(start).toISOString(),
          end: new Date(end).toISOString(),
        });
      }
      fetchEvents();
    } catch (err) {
      alert('Failed to move event');
    }
  };
  const resizeEvent = async ({ event, start, end }) => {
    try {
      await updateCalendarEvent(event.id, {
        summary: event.title,
        start: { dateTime: new Date(start).toISOString() },
        end: { dateTime: new Date(end).toISOString() },
        colorId: event.colorId,
      });
      if (event.taskId) {
        await patchTask(event.taskId, {
          start: new Date(start).toISOString(),
          end: new Date(end).toISOString(),
        });
      }
      fetchEvents();
    } catch (err) {
      alert('Failed to resize event');
    }
  };

  return (
    <div className="card my-4">
      <div className="card-body">
        <h5 className="card-title">Google Calendar (Month/Week/Year Views)</h5>
        <DndProvider backend={HTML5Backend}>
          <DnDCalendar
            ref={calendarRef}
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={{ height: 600 }}
            selectable
            onSelectSlot={handleSelectSlot}
            onDoubleClickEvent={(event) => { setEditEvent(event); setShowEditModal(true); }}
            onContextMenu={handleEventContextMenu}
            views={{ month: true, week: true, day: true, year: true }}
            view={view}
            onView={setView}
            eventPropGetter={(event) => ({ style: { backgroundColor: event.color } })}
            onEventDrop={moveEvent}
            onEventResize={resizeEvent}
            resizable
          />
        </DndProvider>
        <ControlledMenu
          {...menuProps}
          anchorPoint={{ x: menuPosition.x, y: menuPosition.y }}
          onClose={closeMenu}
        >
          <MenuItem onClick={() => { openEditModal(); closeMenu(); }} title="Edit event">
            <FaEdit className="me-2" /> Edit
          </MenuItem>
          <MenuItem onClick={async () => { await handleDelete(); closeMenu(); }} title={contextEvent?.taskId ? "Delete event and linked task" : "Delete event"}>
            <FaTrash className="me-2" /> {contextEvent?.taskId ? 'Delete Event & Task' : 'Delete Event'}
          </MenuItem>
          <MenuItem onClick={handleDuplicate} title="Duplicate event">
            <FaClone className="me-2" /> Duplicate
          </MenuItem>
          <MenuItem onClick={handleMarkImportant} title={contextEvent?.important ? 'Unmark as important' : 'Mark as important'}>
            {contextEvent?.important ? <FaStar className="me-2 text-warning" /> : <FaRegStar className="me-2" />} {contextEvent?.important ? 'Unmark Important' : 'Mark Important'}
          </MenuItem>
          <MenuItem onClick={handleCopyDetails} title="Copy event details">
            <FaCopy className="me-2" /> Copy Details
          </MenuItem>
          <MenuItem onClick={handleExportICS} title="Export as .ics">
            <FaFileExport className="me-2" /> Export (.ics)
          </MenuItem>
          {contextEvent?.meetingLink && (
            <MenuItem onClick={handleJoinMeeting} title="Join meeting">
              <FaExternalLinkAlt className="me-2" /> Join Meeting
            </MenuItem>
          )}
          <MenuItem
            title="Change color"
            submenu={
              <div style={{ display: 'flex', padding: 8 }}>
                {colorOptions.map(color => (
                  <div
                    key={color}
                    onClick={() => handleColorChange(color)}
                    style={{
                      width: 24, height: 24, borderRadius: '50%', background: color, margin: 2, cursor: 'pointer', border: contextEvent?.color === color ? '2px solid #000' : '1px solid #ccc'
                    }}
                    title={color}
                  />
                ))}
              </div>
            }
          >
            <FaPalette className="me-2" /> Change Color
          </MenuItem>
        </ControlledMenu>
        {showForm && (
          <form onSubmit={handleFormSubmit} className="mt-3">
            <div className="mb-2">
              <label>Title</label>
              <input
                name="title"
                className="form-control"
                value={formData.title}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="mb-2">
              <label>Start</label>
              <input
                name="start"
                type="datetime-local"
                className="form-control"
                value={formData.start instanceof Date ? formData.start.toISOString().slice(0,16) : formData.start}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="mb-2">
              <label>End</label>
              <input
                name="end"
                type="datetime-local"
                className="form-control"
                value={formData.end instanceof Date ? formData.end.toISOString().slice(0,16) : formData.end}
                onChange={handleFormChange}
                required
              />
            </div>
            <div className="mb-2">
              <label>Color</label>
              <input
                name="color"
                type="color"
                className="form-control form-control-color"
                value={formData.color}
                onChange={handleFormChange}
              />
            </div>
            <button type="submit" className="btn btn-success me-2">Add Event</button>
            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
          </form>
        )}
        {showEditModal && editEvent && (
          <div className="modal d-block" tabIndex="-1" style={{ background: 'rgba(0,0,0,0.3)' }}>
            <div className="modal-dialog">
              <div className="modal-content">
                <form onSubmit={handleEditSubmit}>
                  <div className="modal-header">
                    <h5 className="modal-title">Edit Event</h5>
                    <button type="button" className="btn-close" onClick={closeEditModal}></button>
                  </div>
                  <div className="modal-body">
                    <div className="mb-2">
                      <label>Title</label>
                      <input
                        name="title"
                        className="form-control"
                        value={editEvent.title}
                        onChange={handleEditChange}
                        required
                      />
                    </div>
                    <div className="mb-2">
                      <label>Start</label>
                      <input
                        name="start"
                        type="datetime-local"
                        className="form-control"
                        value={editEvent.start instanceof Date ? editEvent.start.toISOString().slice(0,16) : editEvent.start}
                        onChange={handleEditChange}
                        required
                      />
                    </div>
                    <div className="mb-2">
                      <label>End</label>
                      <input
                        name="end"
                        type="datetime-local"
                        className="form-control"
                        value={editEvent.end instanceof Date ? editEvent.end.toISOString().slice(0,16) : editEvent.end}
                        onChange={handleEditChange}
                        required
                      />
                    </div>
                    <div className="mb-2">
                      <label>Color</label>
                      <input
                        name="color"
                        type="color"
                        className="form-control form-control-color"
                        value={editEvent.color}
                        onChange={handleEditChange}
                      />
                    </div>
                    {/* Future: Repeating event options */}
                    {/* <div className="mb-2">
                      <label>Repeat</label>
                      <select className="form-control" name="repeat" value={editEvent.repeat || ''} onChange={handleEditChange}>
                        <option value="">None</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div> */}
                  </div>
                  <div className="modal-footer">
                    <button type="submit" className="btn btn-primary">Save</button>
                    <button type="button" className="btn btn-secondary" onClick={closeEditModal}>Cancel</button>
                    <button type="button" className="btn btn-danger ms-auto" onClick={async () => { setContextEvent(editEvent); await handleDelete(); closeEditModal(); }}>
                      Delete
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CalendarPanel; 