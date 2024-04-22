import React from 'react';
import { MenuItem } from '../../types';


interface MenuProps {
    items: MenuItem[];
}

const Menu: React.FC<MenuProps> = ({ items }) => {
    return (
        <ul className='list-unstyled pt-4'>
            {items.map((item, index) => (
                <li key={index} >
                    <a href={item.url} className='pd-4'>
                        <i className={item.icon}></i>
                        {item.label}
                    </a>
                </li>
            ))}
        </ul>
    );
};

export default Menu;