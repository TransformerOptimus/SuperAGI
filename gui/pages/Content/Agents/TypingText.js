import React, { useState, useEffect } from 'react';

const TypingText = ({ text, minWords = 2, maxWords = 4, speed = 200, onComplete, startTyping }) => {
    const [displayText, setDisplayText] = useState('');
    const [typingCompleted, setTypingCompleted] = useState(false);

    useEffect(() => {
        if (startTyping && !typingCompleted) {
            let index = 0;
            const words = text.split(' ');

            const interval = setInterval(() => {
                if (index < words.length) {
                    const groupSize = Math.floor(Math.random() * (maxWords - minWords + 1) + minWords);
                    const group = words.slice(index, index + groupSize).join(' ');
                    setDisplayText((prevDisplayText) => prevDisplayText + ' ' + group);

                    index += groupSize;
                } else {
                    clearInterval(interval);
                    setTypingCompleted(true);
                    if (onComplete) {
                        onComplete();
                    }
                }
            }, speed);

            return () => clearInterval(interval);
        }
    }, [text, minWords, maxWords, speed, onComplete, startTyping, typingCompleted]);

    return <span>{startTyping ? displayText : text}</span>;
};

export default TypingText;