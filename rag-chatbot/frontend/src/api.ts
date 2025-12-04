import axios from 'axios';
import {type Message, ChatResponse, SendPrompt, SessionInfo} from "@/types"

export const getSessions = (id:string) => axios.get<SessionInfo[]>(`${import.meta.env.VITE_API_URL}/api/sessions/${id}`);
export const deleteSession = (id: string) => axios.delete(`${import.meta.env.VITE_API_URL}/api/session/${id}`);
export const sendPrompt = (prompt:SendPrompt, file:File | null) => {
  const formData = new FormData();
  formData.append("question", prompt.question);
  formData.append("session_id", prompt.session_id ?? "");
  formData.append("user_id", prompt.user_id ?? "");
  if (file) formData.append("file", file);
  return axios.post<ChatResponse>(`${import.meta.env.VITE_API_URL}/api/chat`, formData);
};
export const getMessages = (sessionId: string)=> axios.get<Message[]>(`${import.meta.env.VITE_API_URL}/api/messages/${sessionId}`);
export const getAdminUserID = ()=> axios.get<string>(`${import.meta.env.VITE_API_URL}/api/users/admin_user_id`);