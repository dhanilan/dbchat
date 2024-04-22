import React from 'react';
import { MenuItem } from '../../types';


interface MenuProps {
    items: MenuItem[];
}

const Menu: React.FC<MenuProps> = ({ items }) => {
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
        </nav>
    );
};

export default Menu;