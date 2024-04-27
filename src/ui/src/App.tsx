
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Row, Col } from 'react-bootstrap';
import 'boxicons/css/boxicons.min.css';
import { uiStore } from './store/uiStore';
import { conversationStore } from './store/chatConversationStore';
import Menu from './components/menu/menu';
import Home from './pages/home/home';
import Settings from './pages/settings/settings';
import Connections from './pages/connections/connections';

import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";
import { useEffect } from 'react';
import { connectionsStore } from './store/connectionsStore';

function App() {

  const ui = uiStore();
  const conversation = conversationStore();
  const store = connectionsStore();
  useEffect(() => {
    conversation.initialize();
  }, [])


  useEffect(() => {
    conversation.fetchAllConversations();
  }, []);

  useEffect(() => {
    store.initialize();
  }, []);



  return (
    <>


      <Container fluid style={{ height: '100vh' }}>
        <Row className='h-100'>
          <Col xl={2} xs={2} className='h-100' style={{ backgroundColor: '#f9f9f9' }}>
            <Menu items={ui.menuItems} />
          </Col>
          <Col xl={10} xs={10} className='h-100' >
            {/* <BrowserRouter> */}
            <Routes>
              <Route path='/' element={<Home></Home>}>

              </Route>
              <Route path='/settings' element={<Settings></Settings>}>


              </Route>
              <Route path='/connections' element={<Connections></Connections>}>
              </Route>
            </Routes>
            {/* </BrowserRouter> */}
          </Col>
        </Row>
      </Container>

    </>
  )
}

export default App
