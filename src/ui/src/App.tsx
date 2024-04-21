
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button, Container, Row, Col, Form } from 'react-bootstrap';
import 'boxicons/css/boxicons.min.css';


function App() {


  return (
    <>
      <Container fluid style={{ height: '100vh' }}>
        <Row className='h-100'>
          <Col xl={2} xs={2} className='h-100' style={{ backgroundColor: '#f9f9f9' }}>
          </Col>
          <Col xl={10} xs={10} className='h-100' >
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
          </Col>
        </Row>
      </Container>

    </>
  )
}

export default App
