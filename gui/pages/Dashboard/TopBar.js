import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import {useRouter} from 'next/router';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {refreshUrl, openNewTab} from "@/utils/utils";

export default function TopBar({selectedProject, userName, env}) {
  const [dropdown, setDropdown] = useState(false);
  const router = useRouter();

  const logoutUser = () => {
    setDropdown(false);

    if (typeof window === 'undefined') {
      return;
    }

    localStorage.removeItem('accessToken');
    refreshUrl();
    router.reload();
  };

  return (
    <div className="top_bar">
      <div className="top_left">
        <div className="top_bar_section top_bar_input cursor_default">
          <div className="horizontal_container">
            <Image width={14} height={14} src="/images/project.svg" alt="project-icon"/>
            <div className="top_bar_font">{selectedProject?.name || ''}</div>
          </div>
        </div>
        <div className="top_bar_section ml_7 cursor_pointer">
          <Image width={14} height={14} src="/images/widgets.svg" alt="widgets-icon"/>
          <div className="top_bar_font" onClick={() => openNewTab(-4, "Marketplace", "Marketplace", false)}>Marketplace</div>
        </div>
      </div>
      <div className="top_right">
        <Image onClick={() => openNewTab(-3, "Settings", "Settings", false)} className="top_right_icon" width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/>
        <div className="top_right_icon" onMouseEnter={() => setDropdown(true)}
             onMouseLeave={() => setDropdown(false)}>
          <Image width={20} height={20} src="/images/profile_pic.png" alt="dropdown-icon"/>
        </div>
        {dropdown && env === 'PROD' &&
          <div className="mt_30 mr_74" onMouseEnter={() => setDropdown(true)}
               onMouseLeave={() => setDropdown(false)}>
            <ul className="dropdown_container w_120p">
              <li className="dropdown_item" onClick={() => setDropdown(false)}>{userName}</li>
              <li className="dropdown_item" onClick={logoutUser}>Logout</li>
            </ul>
          </div>}
      </div>
      <ToastContainer/>
    </div>
  )
}
