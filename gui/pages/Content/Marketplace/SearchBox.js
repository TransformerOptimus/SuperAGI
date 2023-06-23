import React from 'react';
import styles from './Market.module.css';

export default function SearchBox({onSearch}){
  const handleSearch = (event) => {
    const searchTerm = event.target.value;
    onSearch(searchTerm);
  };
  return (
    <div className={styles.search_box}>
      <input type="text" placeholder="Search here" onChange={handleSearch} />
    </div>
  );
};


