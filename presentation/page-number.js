import React from "react";
import { useDeck } from "mdx-deck"; // Import useDeck

const PageNumber = ({ children }) => {
  const state = useDeck(); // Declare a new state variable

  const currentSlide = state.index + 1; // The slides are zero-index
  return (
      <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{currentSlide}</p>
  );
};

export default PageNumber;
