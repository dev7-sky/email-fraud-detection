import os
import html
import json
def create_viewer(email_list,total_emails,output_folder = "outputs"):
    os.makedirs(output_folder, exist_ok=True)
    index_path = os.path.join(output_folder, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:

        f.write("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Google Takeout Viewer</title>

    <style>

    body{
        margin:0;
        font-family:Arial;
    }
    .header{

        height:60px;

        background:#0F172A;

        color:white;

        display:flex;

        align-items:center;

        justify-content:space-between;

        padding:0 20px;

        font-size:22px;

        font-weight:bold;

        box-shadow:0 2px 8px rgba(0,0,0,.2);

    }

    .logo{

        display:flex;

        align-items:center;

        gap:10px;

    }

    .stats{

        font-size:15px;

        font-weight:normal;

        color:#cbd5e1;

    }

    .container{
        display:flex;
        height:calc(100vh - 60px);
        overflow:hidden;
    }

    .sidebar{

        width:35%;
        min-width:220px;
        max-width:80%;

        background:#F8FAFC;

        display:flex;
        flex-direction:column;

    }

    .sidebar table{
        width:100%;
        border-collapse:collapse;
    }

    .sidebar th,.sidebar td{
        border:1px solid #ddd;
        padding:8px;
    }

    .sidebar tr:hover{
        background:#f5f5f5;
    }

    .viewer{
        flex:1;
        overflow:hidden;
    }

    iframe{
        width:100%;
        height:100%;
        border:none;
    }

    .mail-list{

        flex:1;

        overflow-y:auto;

        padding:10px;

    }

    .mail-card{

        background:white;

        border-radius:10px;

        margin-bottom:10px;

        box-shadow:0 1px 4px rgba(0,0,0,.12);

        transition:.25s;

    }

    .mail-card:hover{

        transform:translateY(-2px);

        box-shadow:0 6px 15px rgba(0,0,0,.18);

    }
    .mail-card.active{

        background:#DBEAFE;

        border-left:5px solid #2563EB;

    }

    .mail-card.active .subject{

        color:#1D4ED8;

    }

    .mail-card a{

        text-decoration:none;

        color:black;

        display:block;

        padding:15px;

    }

    .subject{

        font-size:16px;

        font-weight:bold;

        margin-bottom:8px;

    }

    .sender{

        color:#555;

        font-size:13px;

    }

    .date{

        margin-top:8px;

        color:#777;

        font-size:12px;

    }
                
    .gutter {
        background: #d1d5db;
        cursor: col-resize;
    }

    .gutter:hover {
        background: #2563eb;
    }
                
    .toolbar{

    padding:12px;
    background:#E2E8F0;

    }

    #searchBox{

        width:98%;
        padding:10px;
        font-size:15px;
        border-radius:8px;
        border:1px solid #bbb;

    }
    
    #folderFilter,
    #timeFilter{

        padding:10px;
        border-radius:8px;
        border:1px solid #bbb;
        margin-left:10px;
        font-size:15px;

    }
    #metadata{

    background:white;

    padding:15px 20px;

    border-bottom:1px solid #ddd;

    box-shadow:0 2px 8px rgba(0,0,0,.08);

    }

    #metadata h3{

        margin-top:0;

        margin-bottom:15px;

        color:#2563EB;

    }
    #exportBtn{

        margin-left:20px;

        padding:8px 14px;

        border:none;

        border-radius:8px;

        background:#2563EB;

        color:white;

        cursor:pointer;

        font-weight:bold;

    }

    #exportBtn:hover{

        background:#1D4ED8;

    }

    .meta-row{

        display:flex;

        margin-bottom:8px;

        align-items:flex-start;

    }

    .meta-title{

        width:130px;

        font-weight:bold;

        color:#374151;

        flex-shrink:0;

    }
    .folder-panel{

        padding:10px;

        border-bottom:1px solid #ddd;

        background:white;

    }

    .folder-item{

        display:flex;

        align-items:center;

        gap:12px;

        padding:12px;

        border-radius:10px;

        cursor:pointer;

    }

    .folder-item:hover{

        background:#E5E7EB;

    }

    .active-folder{

        background:#DBEAFE;

        color:#2563EB;

        font-weight:bold;

    }
    .sidebar.collapsed{

        width:70px !important;

    }

    .sidebar.collapsed .folder-item::first-letter{

        font-size:22px;

    }

    .sidebar.collapsed{

        width:75px !important;

    }
    .sidebar.collapsed .folder-item{

        justify-content:center;

    }

    .sidebar.collapsed .folder-item .text{

        display:none;

    }



    </style>

    </head>

    <body>

    """)
        f.write(f"""
    <div class="header">

      <div class="logo">

        <span id="menuBtn" style="cursor:pointer;font-size:24px;margin-right:15px;">
            ☰
        </span>

        🛡️ Google Takeout Email Viewer

    </div>

       <div class="stats">

            Total Emails : {total_emails}

            <button id="exportBtn">
                📄 Export Results
            </button>

        </div>

    </div>

    <div class="toolbar">

    <input
    type="text"
    id="searchBox"
    placeholder="🔍 Search Subject, Sender or Content">

    <label>From:</label>
    <input type="date" id="fromDate">

    <label>To:</label>
    <input type="date" id="toDate">

   

    </div>

   <div class="container">

        <div id="left" class="sidebar">

            <div class="folder-panel">

                <div class="folder-item active-folder" data-folder="all">
                    📬 All
                </div>

                <div class="folder-item" data-folder="Inbox">

                    <span class="icon">📥</span>

                    <span class="text">Inbox</span>

                </div>

                <div class="folder-item" data-folder="Sent">
                    <span class="icon">📤</span>

                    <span class="text">Sent</span>
                </div>

                <div class="folder-item" data-folder="Spam">

                    <span class="icon">🚫</span>

                    <span class="text">Spam</span>

                </div>

                <div class="folder-item" data-folder="Trash">
                    <span class="icon">🗑</span>

                    <span class="text">Trash</span>
                </div>

            </div>

            <div class="mail-list">
    """)

        for email in email_list:
            safe_subject = html.escape(email["subject"], quote=True)
            safe_from = html.escape(email["from"], quote=True)
            safe_to = html.escape(email["to"], quote=True)
            safe_date = html.escape(email["date"], quote=True)
            safe_body = html.escape(email["body"], quote=True)
            safe_labels = html.escape(email["labels"], quote=True)
            safe_timestamp = html.escape(email["timestamp"], quote=True)
            safe_attachments = html.escape(
                json.dumps(email["attachments"]),
                quote=True
            )
            f.write(f"""

                        <div class="mail-card"

                        data-subject="{safe_subject}"
                        data-from="{safe_from}"
                        data-to="{safe_to}"
                        data-date="{safe_date}"
                        data-labels="{safe_labels}"
                        data-body="{safe_body}"
                        data-time="{safe_timestamp}"
                        data-attachments="{safe_attachments}">

                        <a href="{email['file']}" target="viewer">

                        <div class="subject">
                        {safe_subject}
                        </div>

                        <div class="sender">
                        {safe_from}
                        </div>

                        <div class="date">
                        {safe_date}
                        </div>

                        </a>

                        </div>

                        """)

        f.write("""

    </div>

    </div>

    <div class="divider" id="divider"></div>

    <div id="right" class="viewer">

    <div id="metadata">

        <h3>📧 Email Information</h3>

        <div class="meta-row">
            <span class="meta-title">From</span>
            <span id="metaFrom"></span>
        </div>

        <div class="meta-row">
            <span class="meta-title">To</span>
            <span id="metaTo"></span>
        </div>

        <div class="meta-row">
            <span class="meta-title">Subject</span>
            <span id="metaSubject"></span>
        </div>

        <div class="meta-row">
            <span class="meta-title">Date</span>
            <span id="metaDate"></span>
        </div>

        <div class="meta-row">
            <span class="meta-title">Labels</span>
            <span id="metaLabels"></span>
        </div>
        <div class="meta-row">

        <span class="meta-title">Attachments</span>

        <span id="metaAttachments"></span>

        </div>
    </div>

    <iframe
        name="viewer"
        src="email_1.html">
    </iframe>

    </div>

    </div>
                
    <script src="https://unpkg.com/split.js/dist/split.min.js"></script>

    <script>
    Split(['#left', '#right'], {
        sizes: [35, 65],
        minSize: [250, 300],
        gutterSize: 8,
        cursor: 'col-resize'
    });
                
        const searchBox = document.getElementById("searchBox");
        const fromDate = document.getElementById("fromDate");
        const toDate = document.getElementById("toDate");
        const exportBtn = document.getElementById("exportBtn");
        const menuBtn = document.getElementById("menuBtn");
        const sidebar = document.getElementById("left");
                
        const metaFrom = document.getElementById("metaFrom");
        const metaTo = document.getElementById("metaTo");
        const metaSubject = document.getElementById("metaSubject");
        const metaDate = document.getElementById("metaDate");
        const metaLabels = document.getElementById("metaLabels");
        const metaAttachments = document.getElementById("metaAttachments");

        searchBox.addEventListener("keyup", filterEmails);
        fromDate.addEventListener("change", filterEmails);
        toDate.addEventListener("change", filterEmails);

        function filterEmails() {

            let value = searchBox.value.toLowerCase();
            let folder = currentFolder.toLowerCase();
            let from = fromDate.value;
            let to = toDate.value;

            let cards = document.querySelectorAll(".mail-card");

            cards.forEach(card => {

                let subject = card.dataset.subject.toLowerCase();
                let sender = card.dataset.from.toLowerCase();
                let body = card.dataset.body.toLowerCase();
                let labels = card.dataset.labels.toLowerCase();
                let timestamp = card.dataset.time;

                let searchMatch =
                    subject.includes(value) ||
                    sender.includes(value) ||
                    body.includes(value);

                let folderMatch =
                    folder === "all" ||
                    labels.includes(folder);
                
                let timeMatch = true;

                let mailDate = new Date(timestamp);

                if(from){

                    let fromObj = new Date(from);

                    if(mailDate < fromObj){
                        timeMatch = false;
                    }

                }

                if(to){

                    let toObj = new Date(to);

                    toObj.setHours(23,59,59,999);

                    if(mailDate > toObj){
                        timeMatch = false;
                    }

                }
                

                if(searchMatch && folderMatch && timeMatch) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
        
                

            });
            }
    document.querySelectorAll(".mail-card").forEach(card => {

        card.addEventListener("click", function(){
            document.querySelectorAll(".mail-card").forEach(c => {
                c.classList.remove("active");
            });

            card.classList.add("active");
            card.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

            metaFrom.textContent = card.dataset.from;
            metaTo.textContent = card.dataset.to;
            metaSubject.textContent = card.dataset.subject;
            metaDate.textContent = card.dataset.date;
            metaLabels.textContent = card.dataset.labels;
                
           let attachments = JSON.parse(card.dataset.attachments);

            if(attachments.length === 0){

                metaAttachments.textContent = "None";

            }
            else{

                metaAttachments.innerHTML = "";

                attachments.forEach(file => {

                    metaAttachments.innerHTML +=
                        `<div>📎 <a href="${file.path}" target="_blank">${file.name}</a></div>`;

                });

            }
        });

    });
    const firstCard = document.querySelector(".mail-card");

    if(firstCard){
        firstCard.click();
    }
    exportBtn.addEventListener("click", function(){

        let visibleCards = document.querySelectorAll(".mail-card:not([style*='display: none'])");

        let csv = [];

        csv.push("Subject,From,To,Date,Labels,Attachments");

        visibleCards.forEach(card => {

            csv.push([
                card.dataset.subject,
                card.dataset.from,
                card.dataset.to,
                card.dataset.date,
                card.dataset.labels,
                card.dataset.attachments
            ].map(value => `"${(value || "").replace(/"/g,'""')}"`).join(","));

        });

        const blob = new Blob([csv.join("\\r\\n")], {
            type: "text/csv;charset=utf-8;"
        });

        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");

        a.href = url;
        a.download = "filtered_emails.csv";

        document.body.appendChild(a);

        a.click();

        document.body.removeChild(a);

        URL.revokeObjectURL(url);

    });
    menuBtn.addEventListener("click", function(){

        sidebar.classList.toggle("collapsed");

    });
    document.querySelectorAll(".folder-item").forEach(item=>{

        item.addEventListener("click",function(){

            document.querySelectorAll(".folder-item").forEach(i=>{

                i.classList.remove("active-folder");

            });

            this.classList.add("active-folder");

            currentFolder = this.dataset.folder;

            filterEmails();

        });

    });

    </script>
                
    </body>

    </html>

    """)

    print("index.html created successfully.")