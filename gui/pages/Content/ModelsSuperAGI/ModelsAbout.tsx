import React, {useState} from 'react';

export default function ModelsAbout({about_data}: {about_data: String}) {
    return (
        <div id="models_about">
            <div dangerouslySetInnerHTML={{ __html: about_data }} />
        </div>
    )
}
