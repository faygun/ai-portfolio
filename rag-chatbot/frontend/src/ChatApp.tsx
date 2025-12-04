import React, { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Paperclip , Send, Trash2 } from "lucide-react";
import { getSessions, getAdminUserID, sendPrompt, getMessages, deleteSession } from "./api";
import {type Message, SendPrompt, SessionInfo } from "@/types"

const ChatApp: React.FC = () => {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [activeSession, setActiveSession] = useState<SessionInfo | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [userID, setUserID] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Load session history from backend
    getAdminUserID().then((userRes)=>{
      setUserID(userRes.data);
      getSessions(userRes.data).then((res) => {
        setSessions(res.data);
        //setActiveSession(res.data[0] || null);
      })
      .catch((err)=>{
        console.log(err);
      });
    })

  }, []);

  // getSessions(userRes.data).then((res) => {
  //     setSessions(res.data);
  //     //setActiveSession(res.data[0] || null);
  //   })
  //   .catch((err)=>{
  //     console.log(err);
  //   });

  const selectSession = async (session:SessionInfo)=>{
      setActiveSession(session)

      getMessages(session.id).then((res)=>{
        setMessages(res.data)
      });

      setFile(null)
  }

  const createNewSession = async ()=>{
    setActiveSession(null);
    setMessages([]);
    setPrompt("");
    setFile(null)
  }

  const removeSession = async (idx:number, id:string)=>{
    if(confirm("Are you sure to remove this session?")){
      await deleteSession(id).then(()=>{
            setActiveSession(null);
            setMessages([])
            
            const updatedList = [...sessions]; 
            updatedList.splice(idx, 1); 
            setSessions(updatedList);

          }).catch((e)=> {
            console.log(e);
            alert(e.message);
          });
      }
  }

  const sendMessage = async () => {
    if (!prompt.trim()) return;

    setMessages((prev) => [...prev, {role: "human", content: prompt}]);

    const userText = prompt;
    setPrompt("");
    await sendPrompt(new SendPrompt(userID, activeSession?.id ?? null, userText), file).then((res)=>{
      setMessages((prev) => [...prev, { role: "ai", content: res.data.answer }]);
      if(!activeSession || activeSession.id === ''){
        const sessionInfo = new SessionInfo(userID, res.data.session_id, res.data.title); 
        setActiveSession(sessionInfo);
        setSessions((prev) => [sessionInfo, ...prev]);
      }
    }).catch((e)=>{
      console.log(e);
      alert(e.message);
    }).finally(()=> setFile(null));
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div>
      <div className="flex h-screen w-screen">  
        {/* Sidebar */}
        <div className="w-64 border-r border-gray-200 p-4">
          <Button className="flex" onClick={createNewSession} >+ New Session</Button>
        {/* <Button className="flex" variant={"secondary"} >+ Upload Document</Button> */}
          <h2 className="text-xl font-bold mb-4">Sessions</h2>
          <ul>
            {
              sessions.length > 0 ? 
              (sessions.map((session, idx) => (
              <li
                key={idx}
                session-id={session.id}
                className={`cursor-pointer p-2 rounded hover:bg-gray-200 ${activeSession != null && activeSession.id === session.id ? "bg-gray-300" : ""}`}
                onClick={()=> selectSession(session)}
              >
                <Trash2 width={16} height={16} className="flex justify-end" onClick={()=> removeSession(idx, session.id)}/>
                {session.title} 
              </li>
            ))) : (<li></li>)
            }
          </ul>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col p-4">
          <div className="flex-1 overflow-y-auto space-y-2 flex flex-col justify-start">
            {messages.length > 0 ? messages.map((msg, idx) => (
              <Card key={idx} className={msg.role === "human" ? "self-end bg-blue-100" : "self-start bg-gray-100"}>
                <CardContent className="p-3">
                  {msg.content}
                </CardContent>
                <div ref={bottomRef}/>
              </Card>
            )) : (<div className="flex-1 flex items-center justify-center text-gray-400">
      No conversation yet. Start chatting!
    </div>)}
          </div>
          <div className="preview-file">{file?.name}</div>
          {/* Input area */}
          <div className="flex gap-2 mt-4">
            <Input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e)=> e.key === "Enter" ? sendMessage() : false}
              placeholder="Ask something..."
              className="flex-1"
            />
            <label className="flex items-center gap-1 cursor-pointer">
              <Paperclip  />
              <input type="file" className="hidden" onChange={(e) => { 
                console.log(e.target.files)
                return e.target.files && setFile(e.target.files[0]
                )}} />
            </label>
            <Button onClick={sendMessage}>
              <Send className="w-4 h-4 mr-1" /> Send
            </Button>
          </div>
        </div>
      </div>
    </div>
   
  );
};

export default ChatApp;
