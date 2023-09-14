import React, {useState, useEffect} from 'react';
import SideBar from './Dashboard/SideBar';
import Content from './Dashboard/Content';
import TopBar from './Dashboard/TopBar';
import 'bootstrap/dist/css/bootstrap.css';
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import './_app.css'
import Head from 'next/head';
import Image from "next/image";
import {
    getOrganisation,
    getProject,
    validateAccessToken,
    checkEnvironment,
    addUser,
    installToolkitTemplate, installAgentTemplate, installKnowledgeTemplate
} from "@/pages/api/DashboardService";
import {githubClientId} from "@/pages/api/apiConfig";
import {
    getGithubClientId
} from "@/pages/api/DashboardService";
import {useRouter} from 'next/router';
import querystring from 'querystring';
import {refreshUrl, loadingTextEffect} from "@/utils/utils";
import MarketplacePublic from "./Content/Marketplace/MarketplacePublic"
import {toast} from "react-toastify";

export default function App() {
    const [selectedView, setSelectedView] = useState('');
    const [applicationState, setApplicationState] = useState("LOADING");
    const [selectedProject, setSelectedProject] = useState(null);
    const [userName, setUserName] = useState('');
    const [organisationId, setOrganisationId] = useState(null);
    const router = useRouter();

    function fetchOrganisation(userId) {
        getOrganisation(userId)
            .then((response) => {
                setOrganisationId(response.data.id);
            })
            .catch((error) => {
                console.error('Error fetching project:', error);
            });
    }

    useEffect(() => {
        loadingTextEffect('Initializing SuperAGI', setLoadingText, 500);
                if (typeof window !== 'undefined') {
                    localStorage.setItem('applicationEnvironment', env);
                }
                    const queryParams = router.asPath.split('?')[1];
                    const parsedParams = querystring.parse(queryParams);
                    let access_token = parsedParams.access_token || null;

                    if (typeof window !== 'undefined' && access_token) {
                        localStorage.setItem('accessToken', access_token);
                        refreshUrl();
                    }

                    validateAccessToken()
                        .then((response) => {
                            setUserName(response.data.name || '');
                            fetchOrganisation(response.data.id);
                        })
                        .catch((error) => {
                            console.error('Error validating access token:', error);
                        });
    }, []);

    useEffect(() => {
        if (organisationId !== null) {
            getProject(organisationId)
                .then((response) => {
                    setSelectedProject(response.data[0]);
                })
                .catch((error) => {
                    console.error('Error fetching project:', error);
                });
        }
    }, [organisationId]);

    useEffect(() => {
        if (selectedProject !== null) {
            setApplicationState("AUTHENTICATED");
        }
    }, [selectedProject]);

    async function signInUser() {
        let github_client_id = githubClientId();

        // If `github_client_id` does not exist, make the API call
        if (!github_client_id) {
            const response = await getGithubClientId();
            github_client_id = response.data.github_client_id;
        }
        if(!github_client_id) {
            console.error('Error fetching github client id make sure to set it in the config file');
        }
        else {
            window.open(`https://github.com/login/oauth/authorize?scope=user:email&client_id=${github_client_id}`, '_self')
        }
    }

    return (
        <div className="app">
            <Head>
                <title>SuperAGI</title>
                {/* eslint-disable-next-line @next/next/no-page-custom-font */}
                <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
                {/* eslint-disable-next-line @next/next/no-page-custom-font */}
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
                      rel="stylesheet"/>
            </Head>
            <div className="signInStyle">
                <div className="signInTopBar">
                    <div className="superAgiLogo"><Image width={132} height={72} src="/images/sign-in-logo.svg"
                                                         alt="super-agi-logo"/></div>
                </div>
                <div className="signInCenter">
                     <div className="signInWrapper">
                        <button className="signInButton" onClick={signInUser}>
                            <Image width={20} height={20} src="/images/github.svg" alt="github"/>&nbsp;Continue with Github
                        </button>
                        <div className="signInInfo">
                            By continuing, you agree to Super AGI’s Terms of Service and Privacy Policy, and to receive important
                            updates.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}