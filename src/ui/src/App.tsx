
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button, Container, Row, Col, Form } from 'react-bootstrap';


function App() {


  return (
    <>
      <Container fluid style={{ height: '100vh' }}>
        <Row className='h-100'>
          <Col xl={2} xs={2} className='h-100' style={{ backgroundColor: '#f9f9f9' }}>
          </Col>
          <Col xl={10} xs={10} className='h-100'>
            <Container fluid>
              <Container>
                All Messages Appear here
              </Container>
              <Container>
                <Row>
                  Sugesstions...
                </Row>
                <Row>
                  <Col>
                    <Form.Control type="text" placeholder="Type Something to get started" />
                  </Col>
                </Row>
              </Container>
            </Container>
          </Col>
        </Row>
        {/* <Row>
          <Col> <Button variant="primary">Primary</Button>{' '}
            <Button variant="secondary">Secondary</Button>{' '}
            <Button variant="success">Success</Button>{' '}
            <Button variant="warning">Warning</Button>{' '}
            <Button variant="danger">Danger</Button>{' '}
            <Button variant="info">Info</Button>{' '}
            <Button variant="light">Light</Button>{' '}
            <Button variant="dark">Dark</Button> <Button variant="link">Link</Button></Col>
          <Col>2 of 2</Col>
        </Row> */}



      </Container>

    </>
  )
}

export default App
