import React, { useRef, useState, useEffect } from "react";
import "./CustomRange.css";

const CustomRange = () => {
    const inputRef = useRef(null);
    const [trackWidth, setTrackWidth] = useState(0);

    useEffect(() => {
        const updateRangeStyles = () => {
            const value = inputRef.current.value;
            const percentage = (value - inputRef.current.min) / (inputRef.current.max - inputRef.current.min) * 100;
            setTrackWidth(percentage);
        };

        inputRef.current.addEventListener("input", updateRangeStyles);

        // Set the initial styles
        updateRangeStyles();

        return () => inputRef.current.removeEventListener("input", updateRangeStyles);
    }, []);

    return (
        <div className="range-wrapper">
            <input ref={inputRef} type="range" min="0" max="100" className="custom-range" />
            <div className="track-background">
                <div className="track-progress" style={{ width: `${trackWidth}%` }}></div>
            </div>
        </div>
    );
};

export default CustomRange;