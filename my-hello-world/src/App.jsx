import React, { useState, createContext, useContext } from 'react';

const themes = {
  light: {
    background: '#ffffff',
    color: '#000000'
  },
  dark: {
    background: '#121212',
    color: '#ffffff'
  }
};

const ThemeContext = createContext();

export const useTheme = () => useContext(ThemeContext);

function App() {
  const [theme, setTheme] = useState('dark'); // default theme

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div style={{ backgroundColor: themes[theme].background, color: themes[theme].color, height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        <h1>Hello World</h1>
        <button onClick={toggleTheme} style={{ marginTop: 20, padding: '10px 20px', cursor: 'pointer' }}>
          Toggle to {theme === 'dark' ? 'light' : 'dark'} theme
        </button>
      </div>
    </ThemeContext.Provider>
  );
}

export default App;
