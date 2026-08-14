/* =========================================================
   CAMPUSIQ - COMPLETE JAVASCRIPT
   Frontend ↔ Flask Backend
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const OFFICIAL_DOMAIN = "@bitsathy.ac.in";

const HISTORY_DAYS = 15;

/*
    Flask backend API
*/
const API_URL = "http://127.0.0.1:5000/api/ask";

/*
    Browser storage
*/
const STORAGE_USER = "campusIQ_current_user";
const STORAGE_CHATS = "campusIQ_chat_history";


/* =========================================================
   DOM ELEMENTS
========================================================= */

const loginPage = document.getElementById("loginPage");
const welcomePage = document.getElementById("welcomePage");
const appPage = document.getElementById("appPage");

const emailInput = document.getElementById("emailInput");
const loginButton = document.getElementById("loginButton");
const loginError = document.getElementById("loginError");

const enterAppButton = document.getElementById("enterAppButton");

const sidebarUserName =
    document.getElementById("sidebarUserName");

const sidebarUserEmail =
    document.getElementById("sidebarUserEmail");

const userAvatar =
    document.getElementById("userAvatar");

const newChatButton =
    document.getElementById("newChatButton");

const historyButton =
    document.getElementById("historyButton");

const logoutButton =
    document.getElementById("logoutButton");

const chatInput =
    document.getElementById("chatInput");

const sendButton =
    document.getElementById("sendButton");

const messagesContainer =
    document.getElementById("messagesContainer");

const emptyChat =
    document.getElementById("emptyChat");

const historyOverlay =
    document.getElementById("historyOverlay");

const historyList =
    document.getElementById("historyList");

const closeHistory =
    document.getElementById("closeHistory");

const logoutModal =
    document.getElementById("logoutModal");

const cancelLogout =
    document.getElementById("cancelLogout");

const confirmLogout =
    document.getElementById("confirmLogout");

const thankYouModal =
    document.getElementById("thankYouModal");

const continueButton =
    document.getElementById("continueButton");

const mobileMenuButton =
    document.getElementById("mobileMenuButton");

const sidebar =
    document.getElementById("sidebar");

const sidebarOverlay =
    document.getElementById("sidebarOverlay");


/* =========================================================
   APPLICATION STATE
========================================================= */

let currentUser = null;
let currentChat = [];
let currentChatId = null;


/* =========================================================
   INITIALIZE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);


function initialize() {

    loadUser();

    setupEventListeners();

    setupSuggestionButtons();

    setupChatInput();

}


/* =========================================================
   USER
========================================================= */

function loadUser() {

    const savedUser =
        sessionStorage.getItem(STORAGE_USER);

    if (!savedUser) {

        showLoginPage();

        return;
    }

    try {

        currentUser =
            JSON.parse(savedUser);

        showWelcomePage();

    }

    catch (error) {

        console.error(
            "User loading error:",
            error
        );

        sessionStorage.removeItem(
            STORAGE_USER
        );

        showLoginPage();

    }
}


/* =========================================================
   GET NAME FROM EMAIL
========================================================= */

function getNameFromEmail(email) {

    let username =
        email.split("@")[0];

    username =
        username.replace(
            /[._-]+/g,
            " "
        );

    return username
        .trim()
        .split(" ")
        .map(
            word =>
                word.charAt(0).toUpperCase()
                +
                word.slice(1)
        )
        .join(" ");
}


/* =========================================================
   LOGIN
========================================================= */

function login() {

    const email =
        emailInput.value
            .trim()
            .toLowerCase();

    loginError.textContent = "";

    if (!email) {

        loginError.textContent =
            "Please enter your official college email.";

        emailInput.focus();

        return;
    }


    if (!isValidEmail(email)) {

        loginError.innerHTML =
            "🚫 User Unauthorized<br>" +
            "<small>" +
            "CampusIQ is accessible only with an official " +
            "@bitsathy.ac.in email ID." +
            "</small>";

        emailInput.focus();

        return;
    }


    const name =
        getNameFromEmail(email);


    currentUser = {

        email: email,

        name: name,

        loginTime:
            new Date().toISOString()

    };


    sessionStorage.setItem(
        STORAGE_USER,
        JSON.stringify(currentUser)
    );


    currentChat = [];

    currentChatId = null;


    showWelcomePage();

}


/* =========================================================
   VALIDATE EMAIL
========================================================= */

function isValidEmail(email) {

    const emailPattern =
        /^[^\s@]+@bitsathy\.ac\.in$/i;

    return emailPattern.test(email);

}


/* =========================================================
   SHOW LOGIN
========================================================= */

function showLoginPage() {

    loginPage.classList.add("active");

    welcomePage.classList.remove("active");

    appPage.classList.remove("active");

}


/* =========================================================
   SHOW WELCOME
========================================================= */

function showWelcomePage() {

    loginPage.classList.remove("active");

    welcomePage.classList.add("active");

    appPage.classList.remove("active");

}


/* =========================================================
   SHOW APPLICATION
========================================================= */

function showApplication() {

    loginPage.classList.remove("active");

    welcomePage.classList.remove("active");

    appPage.classList.add("active");


    updateUserUI();

    startNewChat();

}


/* =========================================================
   UPDATE USER UI
========================================================= */

function updateUserUI() {

    if (!currentUser) {

        return;
    }


    /*
        Your HTML contains both
        user-name and user-email.

        We display the logged-in
        college email in the first field.
    */

    sidebarUserName.textContent =
        currentUser.email;


    sidebarUserEmail.style.display =
        "none";


    userAvatar.textContent =
        currentUser.email
            .charAt(0)
            .toUpperCase();

}


/* =========================================================
   LOGOUT MODAL
========================================================= */

function openLogoutModal() {

    logoutModal.classList.remove(
        "hidden"
    );

}


function closeLogoutModal() {

    logoutModal.classList.add(
        "hidden"
    );

}


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    /*
        Save current conversation
        before logging out.
    */

    saveCurrentChat();


    /*
        Remove active session.
    */

    sessionStorage.removeItem(
        STORAGE_USER
    );


    currentUser = null;

    currentChat = [];

    currentChatId = null;


    closeLogoutModal();


    appPage.classList.remove(
        "active"
    );

    welcomePage.classList.remove(
        "active"
    );

    loginPage.classList.add(
        "active"
    );


    emailInput.value = "";

    loginError.textContent = "";


    /*
        Show thank-you modal.
    */

    thankYouModal.classList.remove(
        "hidden"
    );

}


/* =========================================================
   THANK YOU MODAL
========================================================= */

function closeThankYou() {

    thankYouModal.classList.add(
        "hidden"
    );

}


/* =========================================================
   NEW CHAT
========================================================= */

function startNewChat() {

    /*
        Save previous chat first.
    */

    saveCurrentChat();


    currentChat = [];

    currentChatId =
        generateChatId();


    renderMessages();

}


/* =========================================================
   GENERATE CHAT ID
========================================================= */

function generateChatId() {

    return (
        "chat_" +
        Date.now() +
        "_" +
        Math.random()
            .toString(36)
            .substring(2, 9)
    );

}


/* =========================================================
   GET ALL CHATS
========================================================= */

function getAllChats() {

    const saved =
        localStorage.getItem(
            STORAGE_CHATS
        );


    if (!saved) {

        return [];

    }


    try {

        const chats =
            JSON.parse(saved);

        return Array.isArray(chats)
            ? chats
            : [];

    }

    catch (error) {

        console.error(
            "Chat history parsing error:",
            error
        );

        return [];

    }

}


/* =========================================================
   SAVE CURRENT CHAT
========================================================= */

function saveCurrentChat() {

    if (
        !currentUser ||
        !currentChat ||
        currentChat.length === 0
    ) {

        return;

    }


    let chats =
        getAllChats();


    const existingIndex =
        chats.findIndex(
            chat =>
                chat.id === currentChatId
        );


    const firstUserMessage =
        currentChat.find(
            message =>
                message.role === "user"
        );


    const title =
        firstUserMessage
            ? firstUserMessage.content
                .substring(0, 50)
            : "New Chat";


    const chatObject = {

        id:
            currentChatId ||
            generateChatId(),

        userEmail:
            currentUser.email,

        title:
            title,

        messages:
            currentChat,

        date:
            new Date().toISOString()

    };


    if (existingIndex >= 0) {

        chats[existingIndex] =
            chatObject;

    }

    else {

        chats.push(
            chatObject
        );

    }


    localStorage.setItem(
        STORAGE_CHATS,
        JSON.stringify(chats)
    );

}


/* =========================================================
   GET LAST 15 DAYS HISTORY
========================================================= */

function getRecentChats() {

    if (!currentUser) {

        return [];

    }


    const chats =
        getAllChats();


    const now =
        new Date();


    const cutoff =
        new Date(
            now.getTime()
            -
            HISTORY_DAYS *
            24 *
            60 *
            60 *
            1000
        );


    return chats

        .filter(
            chat =>
                chat.userEmail ===
                currentUser.email
        )

        .filter(
            chat =>
                new Date(chat.date)
                >= cutoff
        )

        .sort(
            (a, b) =>
                new Date(b.date)
                -
                new Date(a.date)
        );

}


/* =========================================================
   SHOW HISTORY
========================================================= */

function showHistory() {

    /*
        Save current chat before
        opening history.
    */

    saveCurrentChat();


    renderHistory();


    historyOverlay.classList.remove(
        "hidden"
    );

}


/* =========================================================
   CLOSE HISTORY
========================================================= */

function hideHistory() {

    historyOverlay.classList.add(
        "hidden"
    );

}


/* =========================================================
   RENDER HISTORY
========================================================= */

function renderHistory() {

    historyList.innerHTML = "";


    const chats =
        getRecentChats();


    if (chats.length === 0) {

        historyList.innerHTML = `

            <div class="no-history">

                🕘

                <br>
                <br>

                No conversations found
                in the last 15 days.

            </div>

        `;

        return;
    }


    chats.forEach(
        chat => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "history-item";


            const date =
                formatDate(
                    chat.date
                );


            item.innerHTML = `

                <div class="history-title">

                    💬
                    ${escapeHTML(chat.title)}

                </div>

                <div class="history-date">

                    ${escapeHTML(date)}

                </div>

            `;


            item.addEventListener(
                "click",
                () => {

                    loadChat(chat);

                    hideHistory();

                }
            );


            historyList.appendChild(
                item
            );

        }
    );

}


/* =========================================================
   LOAD CHAT
========================================================= */

function loadChat(chat) {

    currentChat =
        Array.isArray(chat.messages)
            ? [...chat.messages]
            : [];


    currentChatId =
        chat.id;


    renderMessages();

}


/* =========================================================
   FORMAT DATE
========================================================= */

function formatDate(dateString) {

    const date =
        new Date(dateString);


    return date.toLocaleString(
        "en-IN",
        {

            day: "2-digit",

            month: "short",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit"

        }
    );

}


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    const text =
        chatInput.value.trim();


    /*
        Do nothing for empty message.
    */

    if (!text) {

        return;

    }


    /*
        User must be logged in.
    */

    if (!currentUser) {

        return;

    }


    /*
        Add user message immediately.
    */

    currentChat.push({

        role: "user",

        content: text

    });


    chatInput.value = "";

    autoResizeTextarea();

    renderMessages();


    /*
        Disable button while backend
        is processing.
    */

    sendButton.disabled = true;

    chatInput.disabled = true;


    /*
        Show temporary loading message.
    */

    const loadingMessage = {

        role: "assistant",

        content:
            "Thinking...",

        source:
            "CampusIQ"

    };


    currentChat.push(
        loadingMessage
    );


    renderMessages();


    try {

        /*
            SEND QUESTION TO FLASK

            POST
            http://127.0.0.1:5000/api/ask
        */

        const response =
            await fetch(
                API_URL,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            question: text,

                            /*
                                Sending email allows
                                the backend to know
                                which user asked.
                            */

                            user_email:
                                currentUser.email

                        })

                }
            );


        /*
            Check HTTP response.
        */

        if (!response.ok) {

            let errorMessage =
                `Backend returned HTTP ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.error) {

                    errorMessage =
                        errorData.error;

                }

            }

            catch (error) {

                /*
                    Response wasn't JSON.
                */

            }


            throw new Error(
                errorMessage
            );

        }


        /*
            Convert response to JSON.
        */

        const data =
            await response.json();


        /*
            Remove "Thinking..."
            message.
        */

        currentChat =
            currentChat.filter(
                message =>
                    message !==
                    loadingMessage
            );


        /*
            Add actual backend answer.
        */

        currentChat.push({

            role: "assistant",

            content:
                data.answer ||
                data.response ||
                "Sorry, I couldn't find an answer.",

            source:
                data.source ||
                "Bannari Amman Institute of Technology",

            source_url:
                data.source_url ||
                data.url ||
                ""

        });


        /*
            Save conversation.
        */

        saveCurrentChat();


        /*
            Render answer.
        */

        renderMessages();

    }

    catch (error) {

        console.error(
            "CampusIQ Backend Error:",
            error
        );


        /*
            Remove loading message.
        */

        currentChat =
            currentChat.filter(
                message =>
                    message !==
                    loadingMessage
            );


        /*
            Add friendly error.
        */

        currentChat.push({

            role: "assistant",

            content:
                "Sorry, I couldn't connect to the CampusIQ college knowledge base. Please make sure the Flask backend is running on http://127.0.0.1:5000.",

            source:
                "CampusIQ Backend"

        });


        saveCurrentChat();

        renderMessages();

    }

    finally {

        /*
            Enable input again.
        */

        sendButton.disabled = false;

        chatInput.disabled = false;

        chatInput.focus();

    }

}


/* =========================================================
   PROTOTYPE RESPONSE
   NOT USED WHEN FLASK BACKEND IS CONNECTED
========================================================= */

function generatePrototypeResponse(question) {

    const lower =
        question.toLowerCase();


    if (
        lower.includes("attendance")
    ) {

        return {

            text:
                "I understand that you're asking about attendance. The official CampusIQ knowledge base will provide the exact attendance rules once the college database is connected.",

            source:
                "College Knowledge Base"

        };

    }


    if (
        lower.includes("exam") ||
        lower.includes("fee")
    ) {

        return {

            text:
                "I understand that you're asking about examinations or fees. Once the official college database is connected, I will retrieve the relevant information and show its source.",

            source:
                "College Knowledge Base"

        };

    }


    if (
        lower.includes("hostel")
    ) {

        return {

            text:
                "I understand that you're asking about hostel information. The official hostel documents will be connected to CampusIQ.",

            source:
                "College Knowledge Base"

        };

    }


    return {

        text:
            "I'm ready to answer your campus-related questions using the official Bannari Amman Institute of Technology knowledge base.",

        source:
            "CampusIQ Knowledge Base"

    };

}


/* =========================================================
   RENDER MESSAGES
========================================================= */

function renderMessages() {

    messagesContainer.innerHTML = "";


    /*
        Empty chat
    */

    if (
        currentChat.length === 0
    ) {

        emptyChat.style.display =
            "flex";

        return;

    }


    emptyChat.style.display =
        "none";


    /*
        Render every message.
    */

    currentChat.forEach(
        message => {

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "message " +
                (
                    message.role === "user"
                        ? "user-message"
                        : "assistant-message"
                );


            const avatar =
                message.role === "user"
                    ? (
                        currentUser &&
                        currentUser.email
                            ? currentUser.email
                                .charAt(0)
                                .toUpperCase()
                            : "U"
                    )
                    : "✦";


            const role =
                message.role === "user"
                    ? "You"
                    : "CampusIQ";


            let sourceHTML = "";


            /*
                SOURCE BOX
            */

            if (message.source) {

                if (message.source_url) {

                    sourceHTML = `

                        <div class="source-box">

                            📚

                            <strong>
                                Source:
                            </strong>

                            ${escapeHTML(
                                message.source
                            )}

                            <br>

                            🔗

                            <a
                                href="${escapeHTML(message.source_url)}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                View Official Source
                            </a>

                        </div>

                    `;

                }

                else {

                    sourceHTML = `

                        <div class="source-box">

                            📚

                            <strong>
                                Source:
                            </strong>

                            ${escapeHTML(
                                message.source
                            )}

                        </div>

                    `;

                }

            }


            wrapper.innerHTML = `

                <div class="message-avatar">

                    ${escapeHTML(avatar)}

                </div>


                <div class="message-content">

                    <div class="message-role">

                        ${escapeHTML(role)}

                    </div>


                    <div>

                        ${formatMessage(
                            message.content
                        )}

                    </div>


                    ${sourceHTML}

                </div>

            `;


            messagesContainer.appendChild(
                wrapper
            );

        }
    );


    scrollToBottom();

}


/* =========================================================
   FORMAT MESSAGE
========================================================= */

function formatMessage(text) {

    if (!text) {

        return "";

    }


    /*
        Escape HTML first.
        This protects the frontend
        from unwanted HTML injection.
    */

    let formatted =
        escapeHTML(String(text));


    /*
        Markdown bold:

        **text**

        → bold
    */

    formatted =
        formatted.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    /*
        Markdown italic:

        *text*

        → italic

        Keep this simple so URLs
        are not affected.
    */

    formatted =
        formatted.replace(
            /(^|[\s>])\*([^*\n]+)\*(?=[\s<]|$)/g,
            "$1<em>$2</em>"
        );


    /*
        Convert URLs into clickable links.
    */

    formatted =
        formatted.replace(
            /(https?:\/\/[^\s<]+)/g,
            function(url) {

                return `
                    <a
                        href="${url}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        ${url}
                    </a>
                `;

            }
        );


    /*
        Convert line breaks.
    */

    formatted =
        formatted.replace(
            /\n/g,
            "<br>"
        );


    return formatted;

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(text) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text;


    return div.innerHTML;

}


/* =========================================================
   SCROLL TO BOTTOM
========================================================= */

function scrollToBottom() {

    const chatArea =
        document.getElementById(
            "chatArea"
        );


    setTimeout(
        () => {

            chatArea.scrollTop =
                chatArea.scrollHeight;

        },
        50
    );

}


/* =========================================================
   CHAT INPUT
========================================================= */

function setupChatInput() {

    chatInput.addEventListener(
        "input",
        autoResizeTextarea
    );


    chatInput.addEventListener(
        "keydown",
        event => {

            /*
                Enter = send
                Shift + Enter = new line
            */

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


/* =========================================================
   AUTO RESIZE TEXTAREA
========================================================= */

function autoResizeTextarea() {

    chatInput.style.height =
        "auto";


    chatInput.style.height =
        Math.min(
            chatInput.scrollHeight,
            150
        )
        + "px";

}


/* =========================================================
   SUGGESTION BUTTONS
========================================================= */

function setupSuggestionButtons() {

    const buttons =
        document.querySelectorAll(
            ".suggestion-card"
        );


    buttons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const question =
                        button.dataset.question;


                    if (!question) {

                        return;

                    }


                    chatInput.value =
                        question;


                    autoResizeTextarea();

                    sendMessage();

                }
            );

        }
    );

}


/* =========================================================
   EVENT LISTENERS
========================================================= */

function setupEventListeners() {


    /*
        LOGIN
    */

    loginButton.addEventListener(
        "click",
        login
    );


    emailInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();

                login();

            }

        }
    );


    /*
        WELCOME
    */

    enterAppButton.addEventListener(
        "click",
        showApplication
    );


    /*
        NEW CHAT
    */

    newChatButton.addEventListener(
        "click",
        () => {

            startNewChat();

            closeMobileSidebar();

        }
    );


    /*
        HISTORY
    */

    historyButton.addEventListener(
        "click",
        () => {

            showHistory();

            closeMobileSidebar();

        }
    );


    closeHistory.addEventListener(
        "click",
        hideHistory
    );


    historyOverlay.addEventListener(
        "click",
        event => {

            if (
                event.target ===
                historyOverlay
            ) {

                hideHistory();

            }

        }
    );


    /*
        SEND
    */

    sendButton.addEventListener(
        "click",
        sendMessage
    );


    /*
        LOGOUT
    */

    logoutButton.addEventListener(
        "click",
        openLogoutModal
    );


    cancelLogout.addEventListener(
        "click",
        closeLogoutModal
    );


    confirmLogout.addEventListener(
        "click",
        logout
    );


    /*
        THANK YOU
    */

    continueButton.addEventListener(
        "click",
        closeThankYou
    );


    /*
        MOBILE MENU
    */

    mobileMenuButton.addEventListener(
        "click",
        openMobileSidebar
    );


    sidebarOverlay.addEventListener(
        "click",
        closeMobileSidebar
    );


    /*
        ESCAPE KEY
    */

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                hideHistory();

                closeLogoutModal();

                closeMobileSidebar();

            }

        }
    );

}


/* =========================================================
   MOBILE SIDEBAR
========================================================= */

function openMobileSidebar() {

    sidebar.classList.add(
        "mobile-open"
    );


    sidebarOverlay.classList.add(
        "active"
    );

}


function closeMobileSidebar() {

    sidebar.classList.remove(
        "mobile-open"
    );


    sidebarOverlay.classList.remove(
        "active"
    );

}


/* =========================================================
   SAVE CHAT WHEN PAGE IS HIDDEN
========================================================= */

window.addEventListener(
    "pagehide",
    () => {

        saveCurrentChat();

    }
);


/* =========================================================
   BEFORE UNLOAD
========================================================= */

window.addEventListener(
    "beforeunload",
    event => {

        /*
            Save chat before leaving.
        */

        saveCurrentChat();


        /*
            Warn the user while logged in.

            Note:
            Modern browsers may ignore the
            custom text and display their own message.
        */

        if (currentUser) {

            event.preventDefault();

            event.returnValue = "";

        }

    }
);


/* =========================================================
   GLOBAL ERROR HANDLING
========================================================= */

window.addEventListener(
    "error",
    event => {

        console.error(
            "CampusIQ JavaScript Error:",
            event.error || event.message
        );

    }
);


window.addEventListener(
    "unhandledrejection",
    event => {

        console.error(
            "CampusIQ Promise Error:",
            event.reason
        );

    }
);
