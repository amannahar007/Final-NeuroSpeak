# NeuroSpeak Dashboard

React + Vite cyberpunk-styled dashboard for real-time EMG visualization.

## Requirements

- Node.js 18 or higher
- npm package manager

## Installation

```bash
cd dashboard
npm install
```

## Configuration

### Socket.io Server URL

Edit `src/App.jsx` to change backend URL:

```javascript
socketRef.current = io('http://localhost:8000')
```

For production, use your backend server IP:
```javascript
socketRef.current = io('http://192.168.1.100:8000')
```

### Vite Proxy (Development Only)

The `vite.config.js` proxies Socket.io requests to backend:

```javascript
proxy: {
  '/socket.io': {
    target: 'http://localhost:8000',
    ws: true
  }
}
```

## Running

### Development Mode
```bash
npm run dev
```

Dashboard will start on `http://localhost:3000`

### Production Build
```bash
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

## Features

### Real-Time EMG Charts
- 3 synchronized line charts (one per sensor)
- 5-second rolling window (~150 data points at 30Hz)
- Cyberpunk color scheme:
  - Sensor 1 (Jaw): Cyan (#00f3ff)
  - Sensor 2 (Chin): Pink (#ff006e)
  - Sensor 3 (Temporal): Purple (#8b5cf6)

### Word Detection Display
- Large animated text display
- Flash animation on new word detection (800ms)
- Shows "---" when idle

### Connection Status
- Green indicator when connected to backend
- Red indicator when disconnected
- Auto-reconnection on connection loss

## Customization

### Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  'cyber-blue': '#00f3ff',
  'cyber-pink': '#ff006e',
  'cyber-purple': '#8b5cf6'
}
```

### Chart Window Size

Edit `src/App.jsx`:

```javascript
// Change 150 to desired number of points
sensor1: [...prev.sensor1.slice(-150), ...]
```

### Animation Duration

Edit `src/components/WordDisplay.jsx`:

```javascript
// Change 800 to desired milliseconds
setTimeout(() => setFlash(false), 800)
```

## Project Structure

```
dashboard/
├── index.html              # HTML entry point
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS config
├── postcss.config.js       # PostCSS config
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Main app component
    ├── index.css           # Tailwind imports
    └── components/
        ├── EMGChart.jsx           # Chart component
        ├── WordDisplay.jsx        # Word display component
        └── ConnectionStatus.jsx   # Connection indicator
```

## Troubleshooting

**Dashboard shows "DISCONNECTED":**
- Ensure backend is running on port 8000
- Check browser console for Socket.io errors
- Verify Socket.io URL in `App.jsx`

**Charts not updating:**
- Check browser console for errors
- Verify backend is emitting `emg_data` events
- Check network tab for WebSocket connection

**Build errors:**
- Delete `node_modules/` and `package-lock.json`
- Run `npm install` again
- Ensure Node.js version is 18+

**Styling not working:**
- Ensure Tailwind CSS is properly configured
- Check `postcss.config.js` exists
- Run `npm run dev` to rebuild

## Development Tips

### Hot Module Replacement (HMR)
Vite provides instant HMR. Changes to components will reflect immediately without full page reload.

### React DevTools
Install React DevTools browser extension for debugging:
- Chrome: [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- Firefox: [React Developer Tools](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

### Performance Monitoring
Open browser DevTools → Performance tab to monitor chart rendering performance.

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

1. Build the project:
```bash
npm run build
```

2. Deploy `dist/` directory

3. Configure environment variable for backend URL

### Docker

See `Dockerfile` in this directory for containerized deployment.

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions

WebSocket support required.
