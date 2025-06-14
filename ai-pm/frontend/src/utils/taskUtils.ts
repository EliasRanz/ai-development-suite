import { Note } from '../types';

/**
 * Check if a task is currently blocked based on its notes
 * A task is considered blocked if the most recent blocking-related note is a blocking note
 */
export const isTaskBlocked = (notes: Note[]): boolean => {
  if (!notes || notes.length === 0) return false;
  
  // Sort notes by creation date, newest first
  const sortedNotes = [...notes].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  
  // Check the most recent blocking-related note
  for (const note of sortedNotes) {
    if (note.content.includes('🚫 BLOCKED:')) {
      return true;
    }
    if (note.content.includes('✅ UNBLOCKED:')) {
      return false;
    }
  }
  
  return false;
};

/**
 * Get the most recent blocking reason from notes
 */
export const getBlockingReason = (notes: Note[]): string | null => {
  if (!notes || notes.length === 0) return null;
  
  // Sort notes by creation date, newest first
  const sortedNotes = [...notes].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  
  // Find the most recent blocking note
  for (const note of sortedNotes) {
    if (note.content.includes('🚫 BLOCKED:')) {
      return note.content.replace('🚫 BLOCKED:', '').trim();
    }
  }
  
  return null;
};
