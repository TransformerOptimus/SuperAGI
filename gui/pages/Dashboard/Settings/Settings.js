import React, {useState, useEffect} from 'react';
import Image from "next/image";
import styles from '../Dashboard.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Settings() {
  return (<>
    <div>Settings</div>
    <ToastContainer/>
  </>)
}