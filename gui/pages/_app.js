import React from 'react';
import App from 'next/app';

class MyApp extends App {
    render() {
        const { Component, pageProps } = this.props;

        return (
            <div>
                <Component {...pageProps} />
            </div>
        );
    }
}

export default MyApp;
