import { useState } from "react";
import "./Tooltip.css";

function Tooltip({ children, content, position = "top" }) {
  const [visible, setVisible] = useState(false);

  return (
    <span
      className="tooltip-wrapper"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && <span className={`tooltip-content tooltip-${position}`}>{content}</span>}
    </span>
  );
}

export default Tooltip;
