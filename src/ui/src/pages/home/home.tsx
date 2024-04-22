import React from 'react';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';

const Home: React.FC = () => {
    return (
        <>
            <Container className='h-100' fluid style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Container>

                </Container>
                <Container className='p-4'>
                    <Row>
                        All Messages Appear here

                    </Row>
                    <Row>
                        Suggestions...
                    </Row>
                    <Row >
                        <Col xl={10}>
                            <Form.Control type="text" placeholder="Type Something to get started" />
                        </Col>
                        <Col xl={2}>
                            <Button type='submit' variant="primary"><i className='bx bx-send'></i> Send</Button>
                        </Col>
                    </Row>
                </Container>
            </Container>
        </>
    );
};

export default Home;