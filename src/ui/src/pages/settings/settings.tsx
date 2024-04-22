import React, { useEffect } from 'react';

import { appSettingStore } from './../../store/appSettingStore';
import { Container } from 'react-bootstrap';

interface SettingsProps {
    // Define your props here
}

const Settings: React.FC<SettingsProps> = () => {
    const store = appSettingStore();

    useEffect(() => {
        store.getAppSetting();
    }
        , []);
    const appSetting = store.appSetting;

    // Add your component logic here

    return (
        <div>
            <Container>
                Seetings:
                <ul>
                    <li>oai_api_key: {appSetting.oai_api_key}</li>
                    <li>analytics_db_url: {appSetting.analytics_db_url}</li>
                    <li>customer_id: {appSetting.customer_id}</li>
                </ul>
            </Container>
        </div>
    );
};

export default Settings;