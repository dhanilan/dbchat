import React, { useEffect, useState } from 'react';

import { Container, Form, Button, Dropdown, DropdownButton, InputGroup } from 'react-bootstrap';
import { connectionsStore } from '../../store/connectionsStore';
import { JsonEditor as Editor } from 'jsoneditor-react';
import 'jsoneditor-react/es/editor.min.css';

interface SettingsProps {
    // Define your props here
}

const Connections: React.FC<SettingsProps> = () => {
    // Add your logic here
    const store = connectionsStore();

    console.log(store.connection);
    const [connections, setConnections] = useState(store.connections);
    const [currentConnection, setCurrentConnection] = useState(store.connection);
    const [loading, setLoading] = useState(store.loading);

    const [name, setName] = useState(store.connection.name);
    const [connectionString, setConnectionString] = useState(store.connection.connection_string);

    const [connectionSchema, setConnectionSchema] = useState(store.connection.connection_schema);


    useEffect(() => {
        setName(store.connection.name);
        setCurrentConnection(store.connection);
        setConnectionString(store.connection.connection_string);
        setConnectionSchema(store.connection.connection_schema);

    }, [store.connection]);

    const handleSubmit = (e: any) => {
        if (!currentConnection.id) {
            return;
        }
        if (!name || !connectionString) {
            alert('Please enter a name and connection string');
        }
        if (!connectionSchema) {
            alert('Please enter a connection schema');
        }
        e.preventDefault();
        store.updateConnection({
            id: currentConnection.id,
            name: name,
            connection_string: connectionString,
            connection_schema: connectionSchema,
            customer_id: store.connection.customer_id,

        });
        console.log('submit');
    }
    const createSchema = () => {
        store.setConnectionDetails({
            id: currentConnection.id,
            name: name,
            connection_string: connectionString,
            connection_schema: store.connection.connection_schema,
            customer_id: store.connection.customer_id,
        });
        store.createSchema();
    }
    const createConnection = () => {
        store.createConnection({ name: 'New Connection' });
    }


    return (
        <div>
            <Container className='pt-4'>
                <h3>Connections</h3>

                <DropdownButton

                    key={currentConnection.name}
                    id={`dropdown-variants-${currentConnection.id}`}
                    variant={currentConnection.name}
                    title={<><i className='bold'>Connection: </i>  <span>{currentConnection.name || 'Select Connection'}</span></>}
                >
                    {store.connections.map((connection, index) => (
                        <Dropdown.Item key={index} active={connection.id == currentConnection.id} eventKey={connection.id} onClick={() => setCurrentConnection(connection)}>{connection.name}
                            <i className='fa fa-trash pl-4 cursor-pointer' onClick={() => store.deleteConnection(connection.id as string)}></i>
                        </Dropdown.Item>
                    ))}

                    <Dropdown.Divider />
                    <Dropdown.Item eventKey="new" onClick={createConnection} >Create New Connection</Dropdown.Item>
                </DropdownButton>

                <Form>

                    <Form.Group controlId="formConnectionName">
                        <Form.Label>Connection Name</Form.Label>
                        <Form.Control type="text" placeholder="Enter connection name" value={name} onChange={(e) => setName(e.currentTarget.value)} />
                    </Form.Group>
                    <InputGroup>


                    </InputGroup>

                    {/* <Form.Group controlId="formConnectionString">


                    </Form.Group> */}

                    <InputGroup>
                        <Form.Label>Database URL. </Form.Label>

                        <br />
                        <Form.Control type="text" placeholder="Enter analytics_db_url" value={connectionString} onChange={(e) => setConnectionString(e.currentTarget.value)} />
                        <Button variant="primary" onClick={createSchema}> Auto-Generate Schema </Button>
                        {/* <Button variant="outline-secondary">Button</Button> */}
                    </InputGroup>

                    <Editor
                        value={{ ...connectionSchema }}

                    />

                    <Button variant="primary" type="submit" onClick={handleSubmit}>
                        Save
                    </Button>
                </Form>
            </Container>
        </div>
    );
}

export default Connections;