document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-demo-btn');
    const overallStatus = document.getElementById('overall-status');
    const terminal = document.getElementById('log-output');

    let eventSource = null;
    let currentAgentId = null;

    function getTimestamp() {
        const now = new Date();
        return now.toTimeString().split(' ')[0];
    }

    function addLog(message, type = 'info') {
        const div = document.createElement('div');
        div.innerHTML = `<span class="log-time">[${getTimestamp()}]</span> <span class="log-${type}">${message}</span>`;
        terminal.appendChild(div);
        terminal.scrollTop = terminal.scrollHeight;
    }

    async function animatePacket(connId) {
        if (!connId) return;
        const connector = document.getElementById(`conn-${connId}`);
        if(!connector) return;
        const packet = connector.querySelector('.data-packet');
        
        packet.style.opacity = '1';
        packet.style.left = '0%';
        
        // Trigger reflow
        void packet.offsetWidth;
        
        packet.style.left = '100%';
        await new Promise(r => setTimeout(r, 1000));
        
        packet.style.opacity = '0';
        packet.style.left = '0%';
    }

    function setAgentState(agentId, state, text) {
        if (!agentId) return;
        const desk = document.getElementById(`agent-${agentId}`);
        if(!desk) return;
        const badge = desk.querySelector('.status-badge');

        desk.classList.remove('working', 'done');
        if (state) {
            desk.classList.add(state);
        }
        badge.textContent = text;
    }

    function parseLogLine(line) {
        // State Machine to map log lines to agents
        
        // Researcher
        if (line.includes('Defence & Current Affairs RSS Fetch') || line.includes('Additional News Sources')) {
            transitionToAgent('researcher');
        }
        // Editor
        else if (line.includes('Daily Post Planning')) {
            transitionToAgent('editor');
        }
        // Designer
        else if (line.includes('Card Background Image Fetch') || line.includes('Card HTML Build') || line.includes('AI Kinetic News Reels')) {
            transitionToAgent('designer');
        }
        // Copywriter
        else if (line.includes('Caption & Card JSON Generation')) {
            transitionToAgent('copywriter');
        }
        // Publisher
        else if (line.includes('Instagram Publishing') || line.includes('Telegram Delivery') || line.includes('YouTube Shorts Publishing')) {
            transitionToAgent('publisher');
        }
        // Pipeline Complete
        else if (line.includes('PIPELINE COMPLETED SUCCESSFULLY') || line.includes('Pipeline completed with return code')) {
            if(currentAgentId) {
                setAgentState(currentAgentId, 'done', 'Completed');
                currentAgentId = null;
            }
            overallStatus.innerHTML = 'Pipeline Completed Successfully! <i class="fa-solid fa-check" style="color: #10b981;"></i>';
            startBtn.innerHTML = 'Restart Pipeline <i class="fa-solid fa-rotate-right"></i>';
            startBtn.disabled = false;
        }
    }

    async function transitionToAgent(newAgentId) {
        if (currentAgentId === newAgentId) return;

        // Finish current agent
        if (currentAgentId) {
            setAgentState(currentAgentId, 'done', 'Completed');
            
            // Pass packet depending on who just finished
            let connId = null;
            if (currentAgentId === 'researcher') connId = 1;
            else if (currentAgentId === 'editor') connId = 2;
            else if (currentAgentId === 'designer') connId = 3;
            else if (currentAgentId === 'copywriter') connId = 4;

            if (connId) {
                await animatePacket(connId);
            }
        }

        // Start new agent
        currentAgentId = newAgentId;
        setAgentState(currentAgentId, 'working', 'Working...');
    }


    function connectToLogStream() {
        if (eventSource) {
            eventSource.close();
        }
        
        eventSource = new EventSource('/stream-logs');
        
        eventSource.onmessage = function(event) {
            if (event.data === ": keepalive") return; // Ignore keepalives
            
            const line = event.data;
            let logType = 'info';
            
            if (line.includes('❌') || line.includes('Error')) logType = 'warn';
            if (line.includes('✅') || line.includes('SUCCESSFULLY')) logType = 'success';

            addLog(line, logType);
            parseLogLine(line);
        };
        
        eventSource.onerror = function() {
            console.error("Lost connection to stream.");
            eventSource.close();
        };
    }

    async function runPipeline() {
        startBtn.disabled = true;
        startBtn.innerHTML = 'Pipeline Running <i class="fa-solid fa-spinner fa-spin"></i>';
        overallStatus.innerHTML = 'Pipeline Execution in Progress...';
        currentAgentId = null;
        
        // Reset all
        document.querySelectorAll('.agent-desk').forEach(desk => {
            desk.classList.remove('working', 'done');
            desk.querySelector('.status-badge').textContent = 'Idle';
        });
        terminal.innerHTML = '';
        addLog('Requesting pipeline start...', 'info');

        try {
            const response = await fetch('/run-pipeline', { method: 'POST' });
            const data = await response.json();
            
            if (data.status === 'success') {
                addLog('Backend confirmed pipeline started.', 'success');
            } else {
                addLog(`Error: ${data.message}`, 'warn');
                startBtn.disabled = false;
                startBtn.innerHTML = 'Initiate Workflow <i class="fa-solid fa-play"></i>';
            }
        } catch (error) {
            addLog(`Network Error: Could not connect to backend.`, 'warn');
            startBtn.disabled = false;
            startBtn.innerHTML = 'Initiate Workflow <i class="fa-solid fa-play"></i>';
        }
    }

    startBtn.addEventListener('click', runPipeline);
    
    // Connect to log stream immediately to catch any ongoing logs
    connectToLogStream();
});
