import React, { useEffect } from 'react';

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

    // Add your component logic here

    return (
        <div>
            <Container className='p-4'>

                <Form>
                    <Form.Group controlId="formBasicEmail">
                        <Form.Label>Open AI API Key</Form.Label>
                        <Form.Control type="text" placeholder="Enter oai_api_key" value={
                            appSetting.oai_api_key} />
                    </Form.Group>
                    <Form.Group controlId="formBasicEmail">
                        <Form.Label>Database URL</Form.Label>
                        <Form.Control type="text" placeholder="Enter analytics_db_url" value={
                            appSetting.analytics_db_url} />
                    </Form.Group>
                    {/* <Form.Group controlId="formBasicEmail">
                        <Form.Label>customer_id</Form.Label>
                        <Form.Control type="text" placeholder="Enter customer_id" value={
                            appSetting.customer_id} />
                    </Form.Group> */}
                    <Button variant="primary" type="submit" className='mt-4'>
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