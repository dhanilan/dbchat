import React, { useEffect, useState } from 'react';

import { Container, Form, Button, Dropdown, DropdownButton, InputGroup } from 'react-bootstrap';
import { Connection, connectionsStore } from '../../store/connectionsStore';
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

        if (store.connection) {
            setName(store.connection.name);
            setCurrentConnection(store.connection);
            setConnectionString(store.connection.connection_string);
            setConnectionSchema(store.connection.connection_schema);
        }

    }, [store, store.connection, store.connection.connection_schema]);

    const handleConnectionChange = (e: Connection) => {
        store.setConnectionDetails(e);

    }

    const handleSubmit = (e: any) => {
        console.log('submit');

        if (!name || !connectionString) {
            alert('Please enter a name and connection string');
            return false;
        }
        if (!connectionSchema || Object.keys(connectionSchema).length === 0) {
            alert('Please enter a valid connection schema');
            return false;
        }


        store.updateConnection({
            id: currentConnection.id,
            name: name,
            connection_string: connectionString,
            connection_schema: store.connection.connection_schema,
            customer_id: store.connection.customer_id,

        });

        e.preventDefault();
    }
    const createSchema = () => {

        store.setCurrentConnection({
            id: currentConnection.id,
            name: name,
            connection_string: connectionString,
            connection_schema: connectionSchema,
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
                {/* <h3>Connections</h3> */}

                <DropdownButton

                    key={currentConnection.name}
                    id={`dropdown-variants-${currentConnection.id}`}
                    variant={currentConnection.name}
                    title={<><span className='font-weight-bold'>Connection: </span>  <span>{currentConnection.name || 'Select Connection'}</span></>}
                >
                    {store.connections.map((connection, index) => (
                        <Dropdown.Item key={index} active={connection.id == currentConnection.id} eventKey={connection.id} onClick={() => handleConnectionChange(connection)}>{connection.name}
                            <i className='fa fa-trash pl-4 cursor-pointer' onClick={() => store.deleteConnection(connection.id as string)}></i>
                        </Dropdown.Item>
                    ))}

                    <Dropdown.Divider />
                    <Dropdown.Item eventKey="new" onClick={createConnection} >Create New Connection</Dropdown.Item>
                </DropdownButton>
                <div className='p-4'>
                    <Form>

                        <Form.Group className="mb-3" controlId="formConnectionName">
                            <Form.Label>Connection Name</Form.Label>
                            <Form.Control type="text" placeholder="Enter connection name" value={name} onChange={(e) => setName(e.currentTarget.value)} />
                        </Form.Group>

                        {/* <Form.Group controlId="formConnectionString">


                    </Form.Group> */}

                        <Form.Group controlId="formConnectionString" className="mb-3" >
                            <Form.Label>Database URL. </Form.Label>

                            <InputGroup>


                                <br />
                                <Form.Control type="text" placeholder="Enter analytics_db_url" value={connectionString} onChange={(e) => setConnectionString(e.currentTarget.value)} />
                                <Button variant="primary" onClick={createSchema}> Auto-Generate Schema </Button>
                                {/* <Button variant="outline-secondary">Button</Button> */}
                            </InputGroup>

                            <Form.Text id="passwordHelpBlock" muted>
                                This should be a valid database connection string. ex:- postgres://user:password@localhost:5432/chinook
                            </Form.Text>

                        </Form.Group>

                        <Form.Group className="mb-3" controlId="exampleForm.ControlTextarea1">
                            <Form.Label>Schema</Form.Label>
                            <Form.Control as="textarea" rows={20} value={JSON.stringify(connectionSchema, null, 2)} onChange={(e) => setConnectionSchema(JSON.parse(e.target.value))} />
                        </Form.Group>
                        {/* <Editor
                        value={connectionSchema}

                    /> */}
                        {/* <Form.Group controlId="formConnectionSchema" className="mb-3">
                            <textarea rows={30} ></textarea>



                        </Form.Group> */}

                        <Button variant="primary" type="submit" onClick={handleSubmit}>
                            Save
                        </Button>
                    </Form>
                </div>
            </Container>
        </div>
    );
}

export default Connections;