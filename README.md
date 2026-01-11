# NXT-Dashboard

A simple, intuitive dashboard for managing Git operations with a beautiful web interface.

## Features

- ✅ View unstaged files
- ✅ Select and stage files with Git Add
- ✅ Responsive loading states (no blank screens!)
- ✅ Clear status messages and error handling
- ✅ Modern, clean UI design

## Getting Started

### Option 1: Direct File Access

Simply open `index.html` in your web browser:

```bash
open index.html
```

### Option 2: Using a Local Server

1. Install dependencies (optional, for live server):
```bash
npm install
```

2. Start the server:
```bash
npm start
```

3. Open your browser to `http://localhost:3000`

## The Fix

This version addresses the "blank screen" issue when pressing Git Add by:

1. **Loading Overlay**: Shows a spinner during operations instead of a blank screen
2. **Error Handling**: Properly catches and displays errors
3. **Async/Await**: Uses modern JavaScript for better control flow
4. **UI Feedback**: Provides clear visual feedback during all operations
5. **State Management**: Properly manages UI state to prevent blank screens

## Usage

1. View your unstaged files in the file list
2. Select the files you want to stage by checking the boxes
3. Click "Git Add Selected" to stage the files
4. The loading spinner will show progress
5. Success message will confirm the operation

No more blank screens!

## Technical Details

- Pure HTML/CSS/JavaScript (no build step required)
- Responsive design
- Modern ES6+ JavaScript
- Simulated Git operations (can be connected to a real Git backend)

## Future Enhancements

- Connect to actual Git backend API
- Add commit functionality
- Show Git history
- Branch management
- Diff viewer
