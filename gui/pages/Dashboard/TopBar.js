import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import {useRouter} from 'next/router';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {refreshUrl, openNewTab, getUserClick} from "@/utils/utils";
import Cookies from 'js-cookie';

export default function TopBar({selectedProject, userName, env}) {
  const [dropdown, setDropdown] = useState(false);
  const router = useRouter();
  const [showDropdown, setShowDropdown] = useState(false)
  const [selectedImagePath, setSelectedImagePath] = useState('/images/agents_icon_dropdown.svg')
  const [selectedOption, setSelectedOption] = useState('Agents')

  const logoutUser = () => {
    setDropdown(false);

    if (typeof window === 'undefined') {
      return;
    }
    getUserClick('Logged Out',{})
    // localStorage.removeItem('accessToken');
    Cookies.set('accessToken', '', { expires: new Date(0),domain: '.superagi.com', path: '/'});
    Cookies.set('Source', 'app.superagi', {domain: '.superagi.com', path: '/'});
    Cookies.set('mixpanel_initialized', 'false', {domain: '.superagi.com', path: '/'});
    refreshUrl();
    router.reload();
  };

  function handleClick (option) {
    if (option === 'Models') {
      setSelectedImagePath("/images/models_icon_dropdown.svg")
      setSelectedOption('Models')
      window.location.href = 'https://models.superagi.com'
    } else {
      setSelectedImagePath("/images/agents_icon_dropdown.svg")
      setSelectedOption('Agents')
    }
    setShowDropdown(false)
  }

  return (
    <div className="top_bar">
      <div className="top_left">
        <div className="top_bar_section cursor_default">
          {env === 'PROD' && false && <div className="horizontal_container">
            <div onClick={() => setShowDropdown(!showDropdown)} className="horizontal_container align-middle cursor-pointer">
              <Image className="mr_8" width={20} height={20} src={selectedImagePath} alt="models-icon" />
              <span className="text_dropdown text_dropdown_18">{selectedOption}</span>
              <Image className="ml_8" width={14} height={14} src="/images/arrow_down.svg" alt="down_arrow" />
            </div>
            {showDropdown && <div className="dropdown_container_models mt_130">
              <ul className="padding_0 margin_0">
                <li className="dropdown_item text_dropdown_15" onClick={() => handleClick('Models')}>
                  <Image className="mr_8" width={20} height={20} src="/images/models_icon_dropdown.svg" alt="models-icon" />
                  <span className="text_dropdown">Models</span>
                </li>
                <li className="dropdown_item text_dropdown_15" onClick={() => handleClick('Agents')}>
                  <Image className="mr_8" width={20} height={20} src="/images/agents_icon_dropdown.svg" alt="agents-icon" />
                  <span className="text_dropdown">Agents</span>
                </li>
              </ul>
            </div>}
          </div>}
        </div>
        {env === 'PROD' && false && <div className="vertical_divider ml_12 mr_20 responsiveness" />}
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
        <div className="horizontal_container gap_20">
          <div className="horizontal_container w_fit_content cursor_pointer gap_4" onClick={() => {window.open("https://superagi.com/docs", "_blank"); getUserClick('SuperAGI Docs Visited', {})}}>
            <Image width={20} height={20} src="/images/docs_icon.svg" alt="docs-icon" />
            <p className="top_bar_font">Docs</p>
          </div>
          <div className="horizontal_container w_fit_content cursor_pointer gap_4" onClick={() => window.open("https://discord.com/invite/dXbRe5BHJC", "_blank")}>
            <Image width={20} height={20} src="/images/discord.svg" alt="discord-icon" />
            <p className="top_bar_font">Get Help</p>
          </div>
          <div className="horizontal_container w_fit_content cursor_pointer gap_4" onClick={() => window.open("https://github.com/TransformerOptimus/SuperAGI", "_blank")}>
            <Image width={20} height={20} src="/images/github_white.svg" alt="github-icon" />
            <p className="top_bar_font">Github</p>
          </div>
        </div>

        <div className="horizontal_bar mr_22 ml_22" />

        <Image onClick={() => {openNewTab(-3, "Settings", "Settings", false); getUserClick('Settings Viewed', {})}} className="top_right_icon" width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/>
        <div className="top_right_icon" onMouseEnter={() => setDropdown(true)}
             onMouseLeave={() => setDropdown(false)}>
          <Image width={20} height={20} src="/images/profile_pic.png" alt="dropdown-icon"/>
        </div>
        {dropdown && env === 'PROD' &&
          <div className="top_bar_profile_dropdown mt_30" onMouseEnter={() => setDropdown(true)}
               onMouseLeave={() => setDropdown(false)}>
            <ul className="dropdown_container w_120p">
              {userName && <li className="dropdown_item" onClick={() => setDropdown(false)}>{userName}</li>}
              <li className="dropdown_item" onClick={logoutUser}>Logout</li>
            </ul>
          </div>}
      </div>
      <ToastContainer/>
    </div>
  )
}
