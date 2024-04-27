import React from 'react';
import { MenuItem } from '../../types';
import { conversationStore } from '../../store/chatConversationStore';

import { useNavigate } from 'react-router-dom';


interface MenuProps {
    items: MenuItem[];
}

const Menu: React.FC<MenuProps> = ({ items }) => {
    const store = conversationStore();

    const allConversations = store.allConversations;
    const navigate = useNavigate();

    const handleItemClick = (id: string) => {
        store.initialize(id);
        navigate(`/`);
    };
    return (
        <nav>

            <h3 className='m-2'>
                <a href='/' className='nav-menu-item pt-4'>
                    <i className='fa fa-home'></i>
                    DB Chat
                </a>
            </h3>

            <ul className='list-unstyled pt-4'>
                <li className={`nav-menu-item pb-2 `} >
                    <a href='#' className='nav-menu-item-link pd-4' onClick={() => store.createConversation()}>
                        <i className='fa fa-plus p-2'></i>
                        New
                    </a>
                </li>
                {allConversations.map((item, index) => (
                    <li key={index} className={`nav-menu-item p-2 ${store.currentConverstationId == item.id ? 'active' : ''}`} >
                        <a href='#' className='nav-menu-item-link pd-4' onClick={() => handleItemClick(item.id)}>

                            {item.title}
                        </a>

                        <a style={{ cursor: 'pointer' }} onClick={() => store.deleteConversation(item.id)}>
                            <i className='fa fa-trash'></i>
                        </a>
                    </li>
                ))}
            </ul>
            <ul className='list-unstyled pt-4'>
                {items.map((item, index) => (
                    <li key={index} className='nav-menu-item pb-2' >
                        <a href={item.url} className='nav-menu-item-link pd-4'>
                            <i className={item.icon}></i>
                            {item.label}
                        </a>
                    </li>
                ))}
            </ul>
        </nav>
    );
};

export default Menu;