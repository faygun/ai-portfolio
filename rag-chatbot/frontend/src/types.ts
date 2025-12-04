export interface Message {
    role: "human" | "ai"
    content:string
}

export class SessionInfo{
  id: string = '';
  title: string = '';
  user_id: string = '';

  constructor(userid:string, id:string, title:string){
    this.title = title;
    this.id = id;
    this.user_id = userid;
  }
}

export class ChatResponse{
    session_id: string = '';
    user_id: string = '';
    answer: string = '';
    title:string = '';
}

export class SendPrompt{
    session_id:string | null;
    user_id:string;
    question:string = '';
    constructor(userid:string, sessionid:string | null, text:string){
        this.session_id = sessionid;
        this.user_id = userid;
        this.question = text;
    }
}
