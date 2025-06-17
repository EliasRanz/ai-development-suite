import { useState, useEffect } from 'react';
import { Task, StatusValue, PriorityValue, UpdateTaskRequest, Note } from '../types';
import { ArrowLeft, Calendar, MessageCircle, Plus, Trash2, AlertTriangle } from 'lucide-react';
import { api } from '../api';
import MarkdownRenderer from './MarkdownRenderer';

interface TaskPageProps {
  task: Task;
  statusValues: StatusValue[];
  priorityValues: PriorityValue[];
  onSave: (task: UpdateTaskRequest) => Promise<void>;
  onBack: () => void;
  isEditMode?: boolean;
  onEditModeChange?: (editing: boolean) => void;
}

export default function TaskPage({ task, statusValues, priorityValues, onSave, onBack, isEditMode = false, onEditModeChange }: TaskPageProps) {
  const [isEditing, setIsEditing] = useState(isEditMode);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [status, setStatus] = useState(task.status);
  const [priority, setPriority] = useState(task.priority);
  const [isSaving, setIsSaving] = useState(false);
  
  // Sync edit mode with external prop
  useEffect(() => {
    setIsEditing(isEditMode);
  }, [isEditMode]);
  
  // Notify parent of edit mode changes
  const updateEditMode = (editing: boolean) => {
    setIsEditing(editing);
    onEditModeChange?.(editing);
  };
  
  // Notes state
  const [notes, setNotes] = useState<Note[]>([]);
  const [notesLoading, setNotesLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [addingNote, setAddingNote] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [blocking, setBlocking] = useState(false);
  const [blockReason, setBlockReason] = useState('');

  // Load notes when component mounts
  useEffect(() => {
    loadNotes();
  }, [task.id]);

  // Helper function to check if task is currently blocked
  const isTaskBlocked = () => {
    return task.is_blocked;
  };

  const loadNotes = async () => {
    try {
      setNotesLoading(true);
      const taskNotes = await api.getTaskNotes(task.id);
      // Sort notes by creation date, newest first
      const sortedNotes = taskNotes.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setNotes(sortedNotes);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setNotesLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    
    try {
      setAddingNote(true);
      const addedNote = await api.createNote(task.id, newNote.trim());
      setNewNote('');
      
      // Optimistically add the note to the list to provide immediate feedback
      setNotes(prevNotes => [addedNote, ...prevNotes]);
      
      // Then reload to ensure consistency with backend
      await loadNotes();
    } catch (error) {
      console.error('Failed to add note:', error);
      // In case of error, reload notes to ensure consistency
      await loadNotes();
    } finally {
      setAddingNote(false);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm('Are you sure you want to delete this note?')) return;
    
    try {
      // Optimistically remove from UI
      setNotes(prevNotes => prevNotes.filter(note => note.id !== noteId));
      
      await api.deleteNote(noteId);
      
      // Reload to ensure consistency
      await loadNotes();
    } catch (error) {
      console.error('Failed to delete note:', error);
      // In case of error, reload notes to restore correct state
      await loadNotes();
    }
  };

  const handleDeleteTask = async () => {
    const taskTitle = task.title;
    const confirmation = prompt(
      `To delete this task, please type the task title exactly as shown:\n\n"${taskTitle}"\n\nType the title below to confirm deletion:`
    );
    
    if (confirmation !== taskTitle) {
      if (confirmation !== null) {
        alert('Task title does not match. Deletion cancelled.');
      }
      return;
    }

    try {
      setDeleting(true);
      await api.updateTaskStatus(task.id, 'deleted');
      onBack(); // Return to the previous view
    } catch (error) {
      console.error('Failed to delete task:', error);
      alert('Failed to delete task. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  const handleBlockTask = async () => {
    if (!blockReason.trim()) {
      alert('Please provide a reason for blocking this task.');
      return;
    }

    try {
      setBlocking(true);
      
      // Block the task using the new API
      await api.blockTask(task.id, blockReason.trim());
      
      // Add a note with the blocking reason for the activity log
      await api.createNote(task.id, `🚫 BLOCKED: ${blockReason.trim()}`);
      
      // Clear the blocking reason input
      setBlockReason('');
      
      // Update the task prop via callback if provided
      if (onSave) {
        await onSave({});
      }
      
      // Reload notes to show the blocking note
      await loadNotes();
    } catch (error) {
      console.error('Failed to block task:', error);
      alert('Failed to block task. Please try again.');
    } finally {
      setBlocking(false);
    }
  };

  const handleUnblockTask = async () => {
    try {
      setBlocking(true);
      
      // Unblock the task using the new API
      await api.unblockTask(task.id);
      
      // Add a note about unblocking for the activity log
      await api.createNote(task.id, '✅ UNBLOCKED: Task can now proceed');
      
      // Update the task prop via callback if provided
      if (onSave) {
        await onSave({});
      }
      
      // Reload notes to show the unblocking note
      await loadNotes();
    } catch (error) {
      console.error('Failed to unblock task:', error);
      alert('Failed to unblock task. Please try again.');
    } finally {
      setBlocking(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave({
        ...(title !== task.title && { title }),
        ...(description !== task.description && { description }),
        ...(status !== task.status && { status }),
        ...(priority !== task.priority && { priority }),
      });
      updateEditMode(false);
    } catch (error) {
      console.error('Failed to save task:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setTitle(task.title);
    setDescription(task.description || '');
    setStatus(task.status);
    setPriority(task.priority);
    updateEditMode(false);
  };

  const getStatusConfig = (statusKey: string) => {
    return statusValues.find(s => s.key === statusKey) || statusValues[0];
  };

  const getPriorityConfig = (priorityKey: string) => {
    return priorityValues.find(p => p.key === priorityKey) || priorityValues[0];
  };

  const statusConfig = getStatusConfig(status);
  const priorityConfig = getPriorityConfig(priority);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-6">
      {/* Unified Header with Title and Metadata */}
      <div className="p-4 mb-1">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-4 flex-1">
            <button
              onClick={onBack}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
              title="Back to board"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">Task #{task.id}</h1>
                <span className="text-sm text-gray-500">•</span>
                <span className="text-sm text-gray-600">{task.project_name}</span>
              </div>
              
              {isEditing ? (
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full text-xl font-semibold p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Task title"
                />
              ) : (
                <h2 className="text-xl font-semibold text-gray-900 mb-2">{task.title}</h2>
              )}
              
              {/* Task Metadata */}
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Created: {formatDate(task.created_at)}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Updated: {formatDate(task.updated_at)}</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Status and Priority in Header - Vertically Stacked */}
          <div className="flex flex-col space-y-2 flex-shrink-0 ml-6">
            {/* Status */}
            <div className="flex flex-col">
              <label className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Status</label>
              {isEditing ? (
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm min-w-[120px]"
                >
                  {statusValues.filter(statusOption => statusOption.key !== 'deleted').map((statusOption) => (
                    <option key={statusOption.key} value={statusOption.key}>
                      {statusOption.label}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-lg min-w-[120px]">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: statusConfig.color }}
                    title={`Task is currently ${statusConfig.label.toLowerCase()}`}
                  />
                  <span className="text-sm font-medium">{statusConfig.label}</span>
                </div>
              )}
            </div>

            {/* Priority */}
            <div className="flex flex-col">
              <label className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Priority</label>
              {isEditing ? (
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm min-w-[120px]"
                >
                  {priorityValues.map((priorityOption) => (
                    <option key={priorityOption.key} value={priorityOption.key}>
                      {priorityOption.label}
                    </option>
                  ))}
                </select>
              ) : (
                <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg min-w-[120px] ${
                  priorityConfig.key === 'critical' ? 'bg-red-50 text-red-700' :
                  priorityConfig.key === 'high' ? 'bg-orange-50 text-orange-700' :
                  priorityConfig.key === 'medium' ? 'bg-yellow-50 text-yellow-700' :
                  priorityConfig.key === 'low' ? 'bg-blue-50 text-blue-700' :
                  'bg-gray-50 text-gray-700'
                }`} title={`This task has ${priorityConfig.label.toLowerCase()} priority`}>
                  {priorityConfig.icon && <span className="text-sm">{priorityConfig.icon}</span>}
                  <span className="text-sm font-medium">{priorityConfig.label}</span>
                </div>
              )}
            </div>
          </div>

          {/* Save/Cancel Controls - Only shown when editing */}
          {isEditing && (
            <div className="flex flex-col space-y-2 flex-shrink-0 ml-4">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 text-sm"
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={handleCancel}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Description and Actions Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        {/* Description - Takes up 3 columns */}
        <div className="lg:col-span-3 bg-white rounded-lg border border-gray-200 p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          {isEditing ? (
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Task description"
            />
          ) : (
            <MarkdownRenderer 
              content={task.description || ''} 
              fallbackText="No description provided."
              className="text-gray-700"
            />
          )}
        </div>

        {/* Actions - Vertically Stacked */}
        <div className="space-y-4">
          {/* Block/Unblock Task */}
          <div className={`rounded-lg border p-4 ${isTaskBlocked() ? 'bg-orange-50 border-orange-200' : 'bg-white border-gray-200'}`}>
            <h3 className={`text-sm font-medium mb-2 flex items-center space-x-2 ${isTaskBlocked() ? 'text-orange-800' : 'text-gray-700'}`}>
              <AlertTriangle className="w-4 h-4" />
              <span>{isTaskBlocked() ? 'Blocked' : 'Block'}</span>
            </h3>
            
            {isTaskBlocked() ? (
              <div>
                <p className="text-xs text-orange-600 mb-2">
                  Reason: {task.blocked_reason}
                </p>
                <button
                  onClick={handleUnblockTask}
                  disabled={blocking}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-1 text-sm"
                >
                  {blocking ? (
                    <span>Unblocking...</span>
                  ) : (
                    <>
                      <span>✅</span>
                      <span>Unblock</span>
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div>
                <p className="text-xs text-gray-600 mb-2">
                  Block if cannot proceed.
                </p>
                <button
                  onClick={() => {
                    const reason = prompt("Reason for blocking (required):");
                    if (reason?.trim()) {
                      setBlockReason(reason);
                      handleBlockTask();
                    }
                  }}
                  disabled={blocking}
                  className="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-1 text-sm"
                >
                  {blocking ? (
                    <span>Blocking...</span>
                  ) : (
                    <>
                      <AlertTriangle className="w-3 h-3" />
                      <span>Block</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Delete Task */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-red-800 mb-2 flex items-center space-x-2">
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </h3>
            <p className="text-xs text-red-700 mb-2">
              Cannot be undone.
            </p>
            <button
              onClick={handleDeleteTask}
              disabled={deleting}
              className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-1 text-sm"
            >
              {deleting ? (
                <span>Deleting...</span>
              ) : (
                <>
                  <Trash2 className="w-3 h-3" />
                  <span>Delete</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Notes Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <MessageCircle className="w-5 h-5" />
            <span>Notes</span>
            <span className="text-sm font-normal text-gray-500">({notes.length})</span>
          </h3>
        </div>

        {/* Add Note Form */}
        <div className="mb-6">
          <div className="flex space-x-3">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add a note..."
              rows={3}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleAddNote}
              disabled={!newNote.trim() || addingNote}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>{addingNote ? 'Adding...' : 'Add'}</span>
            </button>
          </div>
        </div>

        {/* Notes List */}
        {notesLoading ? (
          <div className="text-center py-8 text-gray-500">
            Loading notes...
          </div>
        ) : notes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No notes yet. Add the first one above.
          </div>
        ) : (
          <div className="space-y-4">
            {notes.map((note) => (
              <div key={note.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <MarkdownRenderer 
                      content={note.content} 
                      className="text-gray-800"
                    />
                    <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500">
                      <Calendar className="w-3 h-3" />
                      <span>
                        {new Date(note.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteNote(note.id)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title="Delete note"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
