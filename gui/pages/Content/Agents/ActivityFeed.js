import React, {useEffect, useRef, useState} from 'react';
import styles from './Agents.module.css';
import {getExecutionFeeds, getDateTime} from "@/pages/api/DashboardService";
import Image from "next/image";
import {loadingTextEffect, formatTimeDifference} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";
import {ClipLoader} from 'react-spinners';

export default function ActivityFeed({selectedRunId, selectedView, setFetchedData, agent}) {
  const [loadingText, setLoadingText] = useState("Thinking");
  const [feeds, setFeeds] = useState([]);
  const feedContainerRef = useRef(null);
  const [runStatus, setRunStatus] = useState("CREATED");
  const [prevFeedsLength, setPrevFeedsLength] = useState(0);
  const [scheduleDate, setScheduleDate] = useState(null);
  const [scheduleTime, setScheduleTime] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const interval = window.setInterval(function () {
      fetchFeeds();
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedRunId]);

  function fetchDateTime() {
    getDateTime(agent.id)
      .then((response) => {
        const {start_date, start_time} = response.data;
        setScheduleDate(start_date);
        setScheduleTime(start_time);
      })
      .catch((error) => {
        console.error('Error fetching agent data:', error);
      });
  }

  useEffect(() => {
    loadingTextEffect('Thinking', setLoadingText, 250);

    if (agent?.is_scheduled && !agent?.is_running) {
      fetchDateTime();
    }
  }, []);

  useEffect(() => {
    if (feeds.length !== prevFeedsLength) {
      if (feedContainerRef.current) {
        setTimeout(() => {
          if (feedContainerRef.current !== null) {
            feedContainerRef.current.scrollTo({top: feedContainerRef.current.scrollHeight, behavior: 'smooth'});
            setPrevFeedsLength(feeds.length);
          }
        }, 100);
      }
    }
  }, [feeds]);

  function scrollToTop() {
    if (feedContainerRef.current) {
      setTimeout(() => {
        feedContainerRef.current.scrollTo({top: 0, behavior: 'smooth'});
      }, 100);
    }
  }

  useEffect(() => {
    fetchFeeds();
  }, [selectedRunId])

  useEffect(() => {
    EventBus.emit('reFetchAgents', {});
  }, [runStatus])

  function fetchFeeds() {
    if (selectedRunId !== null) {
      setIsLoading(true);
      getExecutionFeeds(selectedRunId)
        .then((response) => {
          const data = response.data;
          setFeeds(data.feeds);
          setRunStatus(data.status);
          setFetchedData(data.permissions);
          EventBus.emit('resetRunStatus', {executionId: selectedRunId, status: data.status});
          setIsLoading(false); //add this line
        })
        .catch((error) => {
          console.error('Error fetching execution feeds:', error);
          setIsLoading(false); // and this line
        });
    }
  }

  useEffect(() => {
    const updateRunStatus = (eventData) => {
      if (eventData.selectedRunId === selectedRunId) {
        setRunStatus(eventData.status);
      }
    };
    const refreshDate = () => {
      fetchDateTime();
    };

    EventBus.on('updateRunStatus', updateRunStatus);
    EventBus.on('refreshDate', refreshDate);

    return () => {
      EventBus.off('updateRunStatus', updateRunStatus);
      EventBus.off('refreshDate', refreshDate);
    };
  });

  return (<>
    <div style={{overflowY: "auto", maxHeight: '80vh', position: 'relative'}} ref={feedContainerRef}>
      <div style={{marginBottom: '55px'}}>
        {agent?.is_scheduled && !agent?.is_running && !selectedRunId ?
          <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center'}}>
            <Image width={72} height={72} src="/images/eventSchedule.png" alt="github"/>
            <div style={{color: 'white', fontSize: '14px'}}>
              This agent is scheduled to start on {scheduleDate}, at {scheduleTime}
            </div>
          </div> : <div>
            {feeds && feeds.map((f, index) => (<div key={index} className={styles.history_box}
                                                    style={{background: '#272335', padding: '20px', cursor: 'default'}}>
              <div style={{display: 'flex'}}>
                {f.role === 'user' && <div className={styles.feed_icon}>💁</div>}
                {f.role === 'system' && <div className={styles.feed_icon}>🛠️ </div>}
                {f.role === 'assistant' && <div className={styles.feed_icon}>💡</div>}
                <div className={styles.feed_title}>{f?.feed || ''}</div>
              </div>
              <div className={styles.more_details_wrapper}>
                {f.time_difference && <div className={styles.more_details}>
                  <div style={{display: 'flex', alignItems: 'center'}}>
                    <div>
                      <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
                    </div>
                    <div className={styles.history_info}>
                      {formatTimeDifference(f.time_difference)}
                    </div>
                  </div>
                </div>}
              </div>
            </div>))}
            {runStatus === 'RUNNING' &&
              <div className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
                <div style={{display: 'flex'}}>
                  <div style={{fontSize: '20px'}}>🧠</div>
                  <div className={styles.feed_title}><i>{loadingText}</i></div>
                </div>
              </div>}
            {runStatus === 'COMPLETED' &&
              <div className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
                <div style={{display: 'flex'}}>
                  <div style={{fontSize: '20px'}}>🏁</div>
                  <div className={styles.feed_title}><i>All goals completed successfully!</i></div>
                </div>
              </div>}
            {runStatus === 'ITERATION_LIMIT_EXCEEDED' &&
              <div className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
                <div style={{display: 'flex'}}>
                  <div style={{fontSize: '20px'}}>⚠️</div>
                  <div className={styles.feed_title}><i>Stopped: Maximum iterations exceeded!</i></div>
                </div>
              </div>}
          </div>
        }
        {feeds.length < 1 && !agent?.is_running && !agent?.is_scheduled &&
             <div style={{
              color: 'white',
              fontSize: '14px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              width: '100%'
            }}>The Agent is not scheduled</div>
        }
      </div>
      {feedContainerRef.current && feedContainerRef.current.scrollTop >= 1200 &&
        <div className="back_to_top" onClick={scrollToTop}
             style={selectedView !== '' ? {right: 'calc(39% - 5vw)'} : {right: '39%'}}>
          <Image width={15} height={15} src="/images/backtotop.svg" alt="back-to-top"/>
        </div>}
    </div>
  </>)
}