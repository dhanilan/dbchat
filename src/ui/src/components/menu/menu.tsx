import React from 'react';
import { MenuItem } from '../../types';
import { conversationStore } from '../../store/chatConversationStore';

interface MenuProps {
    items: MenuItem[];
}

const Menu: React.FC<MenuProps> = ({ items }) => {
    const store = conversationStore();
    const allConversations = store.allConversations;
    return (
        <nav>
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
            <h5>Conversations</h5>

            <ul className='list-unstyled pt-4'>
                <li className='nav-menu-item pb-2' >
                    <a href='#' className='nav-menu-item-link pd-4' onClick={() => store.createConversation()}>
                        <i className='fa fa-plus p-2'></i>
                        New Conversation
                    </a>
                </li>
                {allConversations.map((item, index) => (
                    <li key={index} className='nav-menu-item pb-2' >
                        <a href='#' className='nav-menu-item-link pd-4' onClick={() => store.initialize(item.id)}>
                            <i className='fa fa-comments p-2'></i>
                            {item.title}
                        </a>
                        &nbsp;
                        <a style={{ cursor: 'pointer' }} onClick={() => store.deleteConversation(item.id)}>
                            <i className='fa fa-trash'></i>
                        </a>
                    </li>
                ))}
            </ul>
        </nav>
    );
};

export default Menu;