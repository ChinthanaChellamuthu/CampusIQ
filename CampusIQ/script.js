/* =========================================================
   CAMPUSIQ
   MAIN JAVASCRIPT
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const OFFICIAL_DOMAIN = "@bitsathy.ac.in";

const HISTORY_DAYS = 15;


/*
    IMPORTANT

    sessionStorage:
    Stores login only for the current browser tab/session.

    localStorage:
    Stores chat history so that history can remain available.
*/

const STORAGE_USER =
    "campusIQ_current_user";

const STORAGE_CHATS =
    "campusIQ_chat_history";


/* =========================================================
   DOM ELEMENTS
========================================================= */

const loginPage =
    document.getElementById("loginPage");

const welcomePage =
    document.getElementById("welcomePage");

const appPage =
    document.getElementById("appPage");


const emailInput =
    document.getElementById("emailInput");

const loginButton =
    document.getElementById("loginButton");

const loginError =
    document.getElementById("loginError");


const enterAppButton =
    document.getElementById("enterAppButton");


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

    /*
        Check only the current session.

        If the user closed the previous tab,
        sessionStorage will be empty and
        CampusIQ will show the login page.
    */

    loadUser();

    setupEventListeners();

    setupSuggestionButtons();

    setupChatInput();
}


/* =========================================================
   USER FUNCTIONS
========================================================= */

function loadUser() {

    const savedUser =
        sessionStorage.getItem(
            STORAGE_USER
        );


    /*
        No active session
        → Show login page
    */

    if (!savedUser) {

        showLoginPage();

        return;
    }


    try {

        currentUser =
            JSON.parse(savedUser);


        /*
            If a valid session exists,
            show the welcome page.
        */

        showWelcomePage();

    }

    catch (error) {

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


    /*
        Empty email
    */

    if (!email) {

        loginError.textContent =
            "Please enter your official college email.";

        emailInput.focus();

        return;
    }


    /*
        Check official college email
    */

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


    /*
        Create current user.

        The name is still kept internally
        because the sidebar can display it.

        It is NOT displayed on the
        Welcome Back page.
    */

    const name =
        getNameFromEmail(email);


    currentUser = {

        email:
            email,

        name:
            name,

        loginTime:
            new Date().toISOString()
    };


    /*
        IMPORTANT:
        sessionStorage instead of localStorage.

        This means the user must sign in again
        when the website session/tab ends.
    */

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

    loginPage.classList.add(
        "active"
    );

    welcomePage.classList.remove(
        "active"
    );

    appPage.classList.remove(
        "active"
    );
}


/* =========================================================
   SHOW WELCOME
========================================================= */

function showWelcomePage() {

    loginPage.classList.remove(
        "active"
    );

    welcomePage.classList.add(
        "active"
    );

    appPage.classList.remove(
        "active"
    );

    /*
        No name is inserted here.

        The HTML simply displays:
        "Welcome back!"
    */
}


/* =========================================================
   SHOW APPLICATION
========================================================= */

function showApplication() {

    loginPage.classList.remove(
        "active"
    );

    welcomePage.classList.remove(
        "active"
    );

    appPage.classList.add(
        "active"
    );


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

    // Show only email
    sidebarUserName.textContent =
        currentUser.email;

    // Hide duplicate email field
    sidebarUserEmail.style.display =
        "none";

    // Avatar = first letter of email
    userAvatar.textContent =
        currentUser.email
            .charAt(0)
            .toUpperCase();
}


/* =========================================================
   LOGOUT
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


function logout() {

    /*
        Save current chat before logout.
    */

    saveCurrentChat();


    /*
        Remove only the active login session.

        Chat history remains.
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
        Show Thank You message.
    */

    thankYouModal.classList.remove(
        "hidden"
    );
}


/* =========================================================
   THANK YOU
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
   CHAT STORAGE
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

        return JSON.parse(saved);

    }

    catch (error) {

        return [];
    }
}


/* =========================================================
   SAVE CHAT
========================================================= */

function saveCurrentChat() {

    if (
        !currentUser ||
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

                    ${date}

                </div>

            `;


            item.addEventListener(
                "click",
                () => {

                    loadChat(
                        chat
                    );

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
        [...chat.messages];


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

            day:
                "2-digit",

            month:
                "short",

            year:
                "numeric",

            hour:
                "2-digit",

            minute:
                "2-digit"
        }
    );
}


/* =========================================================
   SEND MESSAGE
========================================================= */

/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage() {

    const text =
        chatInput.value.trim();

    if (!text) {
        return;
    }

    if (!currentUser) {
        return;
    }

    /* Add user message */

    currentChat.push({
        role: "user",
        content: text
    });

    chatInput.value = "";

    autoResizeTextarea();

    renderMessages();


    /*
        CONNECT TO CAMPUSIQ BACKEND

        Flask backend:
        http://127.0.0.1:5000/api/ask
    */

    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: text
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Backend request failed"
            );
        }


        const data =
            await response.json();


        /*
            Backend answer
        */

       currentChat.push({

    role: "assistant",

    content:
        data.answer ||
        "Sorry, I couldn't find an answer.",

    source:
        data.source ||
        "Bannari Amman Institute of Technology",

    source_url:
        data.source_url || ""
});


        saveCurrentChat();

        renderMessages();

    }

    catch (error) {

        console.error(
            "CampusIQ Backend Error:",
            error
        );


        currentChat.push({

            role: "assistant",

            content:
                "Sorry, I couldn't connect to the CampusIQ college knowledge base. Please make sure the backend server is running.",

            source:
                "CampusIQ Backend"
        });


        saveCurrentChat();

        renderMessages();
    }
}

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
                "College Knowledge Base — To be connected"

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
                "College Knowledge Base — To be connected"

        };
    }


    if (
        lower.includes("hostel")
    ) {

        return {

            text:
                "I understand that you're asking about hostel information. The official hostel documents will be connected to CampusIQ in the next stage.",

            source:
                "College Knowledge Base — To be connected"

        };
    }


    return {

        text:
            "I'm ready to answer your campus-related questions. The official Bannari Amman Institute of Technology knowledge base will be connected in the next stage. Once connected, I will answer using the database and show the relevant source.",

        source:
            "CampusIQ Knowledge Base — To be connected"

    };
}


/* =========================================================
   RENDER MESSAGES
========================================================= */

function renderMessages() {

    messagesContainer.innerHTML =
        "";


    if (
        currentChat.length === 0
    ) {

        emptyChat.style.display =
            "flex";

        return;
    }


    emptyChat.style.display =
        "none";


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
                    ? "U"
                    : "✦";


            const role =
                message.role === "user"
                    ? "You"
                    : "CampusIQ";


            let sourceHTML = "";

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

    } else {

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

                    ${avatar}

                </div>


                <div class="message-content">

                    <div class="message-role">

                        ${role}

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
        First escape HTML for security.
        This prevents backend/user text from being
        interpreted as unwanted HTML.
    */

    let formatted =
        escapeHTML(text);


    /*
        Convert Markdown bold:

        **text**

        into:

        <strong>text</strong>
    */

    formatted =
        formatted.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    /*
        Convert URLs into clickable links.
    */

    formatted =
        formatted.replace(
            /(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
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
   SCROLL
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


function autoResizeTextarea() {

    chatInput.style.height =
        "auto";


    chatInput.style.height =
        Math.min(
            chatInput.scrollHeight,
            150
        )
        +
        "px";
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


    /* LOGIN */

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

                login();

            }

        }
    );


    /* WELCOME */

    enterAppButton.addEventListener(
        "click",
        showApplication
    );


    /* NEW CHAT */

    newChatButton.addEventListener(
        "click",
        () => {

            startNewChat();

            closeMobileSidebar();

        }
    );


    /* HISTORY */

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


    /* SEND */

    sendButton.addEventListener(
        "click",
        sendMessage
    );


    /* LOGOUT */

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


    /* THANK YOU */

    continueButton.addEventListener(
        "click",
        closeThankYou
    );


    /* MOBILE */

    mobileMenuButton.addEventListener(
        "click",
        openMobileSidebar
    );


    sidebarOverlay.addEventListener(
        "click",
        closeMobileSidebar
    );


    /* ESCAPE */

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
   TAB CLOSE WARNING
========================================================= */

/*
    Browser controls the exact text of this warning.

    When the user tries to close/leave the page while
    logged in, the browser may show its own confirmation.

    Because the user session is stored in sessionStorage,
    closing the tab ends that session.
*/

window.addEventListener(
    "beforeunload",
    event => {

        if (currentUser) {

            event.preventDefault();

            event.returnValue =
                "Please logout from CampusIQ before closing.";

            return event.returnValue;
        }

    }
);


/* =========================================================
   SAVE CHAT BEFORE PAGE HIDDEN
========================================================= */

window.addEventListener(
    "pagehide",
    () => {

        saveCurrentChat();

    }
);