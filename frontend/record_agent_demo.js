const { launch, getStream } = require("puppeteer-stream");
const fs = require("fs");
const path = require("path");

(async () => {
  console.log("Launching browser with puppeteer-stream...");
  const browser = await launch({
    executablePath: "/usr/bin/google-chrome",
    headless: "new",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--window-size=1280,800",
      "--autoplay-policy=no-user-gesture-required",
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Navigate to live Cloud Run service
  await page.goto("https://it-helpdesk-frontend-548260681732.us-east1.run.app", { waitUntil: "networkidle2" });

  // Setup video output stream
  const videoPath = path.join(__dirname, "demo_recording.webm");
  const fileStream = fs.createWriteStream(videoPath);

  const stream = await getStream(page, {
    audio: true,
    video: true,
    mimeType: "video/webm",
  });
  stream.pipe(fileStream);

  console.log("Recording started...");

  // Start background lo-fi music inside page context
  await page.evaluate(() => {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    function playLofiChord(time, freqs) {
      freqs.forEach(freq => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, time);
        
        gain.gain.setValueAtTime(0.06, time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 1.2);
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(time);
        osc.stop(time + 1.2);
      });
    }

    function playBeat(time) {
      const kick = audioCtx.createOscillator();
      const kGain = audioCtx.createGain();
      kick.frequency.setValueAtTime(120, time);
      kick.frequency.exponentialRampToValueAtTime(30, time + 0.15);
      kGain.gain.setValueAtTime(0.2, time);
      kGain.gain.exponentialRampToValueAtTime(0.001, time + 0.15);
      kick.connect(kGain);
      kGain.connect(audioCtx.destination);
      kick.start(time);
      kick.stop(time + 0.15);
    }

    const chords = [
      [261.63, 329.63, 392.00, 493.88], // Cmaj7
      [220.00, 261.63, 329.63, 392.00], // Am7
      [174.61, 220.00, 261.63, 329.63], // Fmaj7
      [196.00, 246.94, 293.66, 349.23], // G7
    ];

    setInterval(() => {
      const now = audioCtx.currentTime;
      chords.forEach((chord, idx) => {
        playLofiChord(now + idx * 0.8, chord);
        playBeat(now + idx * 0.8);
      });
    }, 3200);
  });

  // Pause briefly
  await new Promise(r => setTimeout(r, 2000));

  // Prompt 1: Show core app capability (System diagnostics)
  console.log("Executing Prompt 1: Check system status...");
  await page.type('#input', 'Check system operational status', { delay: 60 });
  await page.click('#form button');
  await new Promise(r => setTimeout(r, 6000));

  // Prompt 2: Richer prompt showing tool call & IT diagram generation
  console.log("Executing Prompt 2: Generate IT diagram for VPN setup...");
  await page.type('#input', 'Generate an IT diagram for VPN network setup and search knowledge base', { delay: 50 });
  await page.click('#form button');
  await new Promise(r => setTimeout(r, 14000));

  console.log("Stopping recording...");
  await stream.destroy();
  fileStream.end();
  await browser.close();
  console.log("Demo recording saved successfully to:", videoPath);
})();
