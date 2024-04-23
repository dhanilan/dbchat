import React, { useEffect, useState } from 'react';

import { appSettingStore } from './../../store/appSettingStore';
import { Container, Form, Button } from 'react-bootstrap';

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
    const [oai_api_key, setOaiApiKey] = useState('');
    const [analytics_db_url, setAnalyticsDbUrl] = useState('');

    useEffect(() => {
        setOaiApiKey(store.appSetting.oai_api_key);
        setAnalyticsDbUrl(store.appSetting.analytics_db_url);
    }, [appSetting]);

    // setOaiApiKey(appSetting.oai_api_key);
    // setAnalyticsDbUrl(appSetting.analytics_db_url);

    const onApiKeyChange = (e: any) => {
        setOaiApiKey(e.target.value);
    }
    const onDbUrlChange = (e: any) => {

        setAnalyticsDbUrl(e.target.value);
    }

    // Add your component logic here
    const onsubmitClick = (e: any) => {
        store.updateAppSetting({ oai_api_key, analytics_db_url });
        e.preventDefault();
        console.log('submit');
    }

    return (
        <div>
            <Container className='p-4'>

                <Form>
                    <Form.Group controlId="formBasicEmail">
                        <Form.Label>Open AI API Key</Form.Label>
                        <Form.Control type="text" placeholder="Enter oai_api_key" value={
                            oai_api_key} onChange={onApiKeyChange} />
                    </Form.Group>
                    <Form.Group controlId="formBasicEmail">
                        <Form.Label>Database URL</Form.Label>
                        <Form.Control type="text" placeholder="Enter analytics_db_url" value={
                            analytics_db_url} onChange={onDbUrlChange} />
                    </Form.Group>
                    {/* <Form.Group controlId="formBasicEmail">
                        <Form.Label>customer_id</Form.Label>
                        <Form.Control type="text" placeholder="Enter customer_id" value={
                            appSetting.customer_id} />
                    </Form.Group> */}
                    <Button variant="primary" type="submit" className='mt-4' onClick={onsubmitClick}>
                        Submit
                    </Button>
                </Form>
                {/* Seetings:
                <ul>
                    <li>oai_api_key: {appSetting.oai_api_key}</li>
                    <li>analytics_db_url: {appSetting.analytics_db_url}</li>
                    <li>customer_id: {appSetting.customer_id}</li>
                </ul> */}
            </Container>
        </div>
    );
};

export default Settings;