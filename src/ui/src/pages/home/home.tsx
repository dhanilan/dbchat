import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { conversationStore } from '../../store/chatConversationStore';

const Home: React.FC = () => {

    const store = conversationStore();
    const [message, setMessage] = useState('');
    const conversationId = store.currentConverstationId;
    const messages = store.messages;
    const wait_for_server = store.wait_for_server;
    useEffect(() => {
        store.initialize();
    }, []);

    const onMessageChange = (event: any) => {
        setMessage(event.target.value);
    }

    const onMessageSubmit = (event: any) => {
        console.log('Button Clicked');
        setMessage('');
        store.addMessage({
            conversationId: conversationId,
            text: message,
            sender: 'User',
            isUser: true,
            timestamp: new Date(),
        });
        event.preventDefault();

    }
    return (
        <>
            <Container className='h-100' fluid style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Container>
                    {/* <Row>
                        <Col xl={12} className='pb-4'>
                            <h1>Chat with us</h1>
                            <h3>Ask what you what to know about your data</h3>
                        </Col>
                    </Row> */}
                </Container>
                <Container className='p-4'>
                    <Row>
                        <Container>

                        </Container>

                    </Row>
                    <Row>
                        <Container>
                            <Row>

                                {messages.map((message) => (

                                    <Col xl={12} key={message.id}>
                                        <Container>
                                            <Row>
                                                <Col xl={12} className='pb-1 font-weight-bold'>
                                                    {message.sender === 'User' ?
                                                        <i className='bx bx-user' ></i> : <i className='bx bxs-bot'></i>}
                                                    &nbsp;
                                                    {message.sender === 'User' ? 'You' : message.sender}
                                                </Col>
                                            </Row>
                                            <Row>
                                                <Col xl={12} className='pb-4 pl-4'>
                                                    &nbsp;&nbsp;{message.text}
                                                </Col>
                                            </Row>
                                        </Container>
                                    </Col>
                                ))}
                            </Row>
                        </Container>
                    </Row>
                    <Row >
                        <Form>
                            <Container>
                                <Row>
                                    <Col xl={10}>
                                        <Form.Control value={message} onChange={onMessageChange} type="text" placeholder="Type Something to get started" />
                                    </Col>
                                    <Col xl={2}>
                                        <Button type='submit' variant="primary" onClick={onMessageSubmit}><i className='bx bx-send'></i> Send</Button>
                                    </Col>
                                </Row>
                            </Container>

                        </Form>

                    </Row>
                </Container>
            </Container>
        </>
    );
};

export default Home;