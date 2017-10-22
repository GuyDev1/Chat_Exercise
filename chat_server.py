import socket
import select
import datetime
server_socket=socket.socket()

server_socket.bind(('127.0.0.1',23))

server_socket.listen(5)
open_client_sockets = []
messages_to_send = []
chat_clients={}
chat_managers=[]
silent_clients=[]
num=0
previous_sender=''
def send_waiting_messages(wlist):
    global previous_sender
    for message in messages_to_send:
       (sender,msg)=message
       if('\r' in msg):
           if(msg=='\r'):
               messages_to_send.remove(message)
               continue
           else:
               msg=msg[1:]
           print msg

       if('view-managers' in msg):
           i=1
           sender.send('NL')
           for manager in chat_managers:
               sender.send('Manager {0} is: {1}, '.format(i,chat_clients[manager]))
               i+=1
           messages_to_send.remove(message)
           previous_sender=sender
           continue
       elif(sender in silent_clients and msg!='quit'):
           sender.send('NL')
           sender.send('You have been muted!')
           messages_to_send.remove(message)
           continue
       elif(msg=='quit'):
           chat_cmd=''
           pass
       else:
           nick_len = int(msg[:2])
           nick = msg[2:2 + nick_len]
           if(sender not in chat_managers and nick[0]=='@'):
               nick=nick[1:]
           chat_cmd = msg[2 + nick_len:2+1 + nick_len]
           chat_msg_len = int(msg[3 + nick_len:5 + nick_len])
           chat_msg = msg[5 + nick_len:5 + nick_len + chat_msg_len]
           chat_clients[sender]=nick
           if(sender in chat_managers):
               nick='@'+nick
           if(chat_cmd=='5'):
               p_msg_len=int(msg[5+nick_len+chat_msg_len:7+nick_len+chat_msg_len])
               p_msg=msg[7+nick_len+chat_msg_len:7+nick_len+chat_msg_len+p_msg_len]
       for client in wlist:
           if (msg == 'quit' and chat_cmd!=3):
               if (sender is not client):
                   client.send(('{:02d}:{:02d} {} has left the chat!'.format(datetime.datetime.now().hour,
                                                                             datetime.datetime.now().minute,
                                                                             chat_clients[sender])))
           elif(chat_cmd=='3'):
               if(sender in chat_managers):
                   try:
                       if (client is chat_clients.keys()[chat_clients.values().index(chat_msg)]):
                           client.send('You have been kicked from the chat!')
                           client.send('quit')
                           open_client_sockets.remove(client)
                       elif(sender is client):
                           sender.send('NL')
                           client.send('{:02d}:{:02d} {} has been kicked from the chat!'.format(datetime.datetime.now().hour,
                                                                                        datetime.datetime.now().minute,
                                                                                        chat_msg))
                       else:
                           client.send('{:02d}:{:02d} {} has been kicked from the chat!'.format(datetime.datetime.now().hour,
                                                                                        datetime.datetime.now().minute,
                                                                                        chat_msg))
                   except:
                       sender.send('NL')
                       sender.send(r"You're not allowed to kick this person from the chat!")
                       break

           else:
               if (chat_cmd == '1'):
                   pass
               elif (chat_cmd == '2'):
                   if(sender in chat_managers):
                       chat_managers.append(chat_clients.keys()[chat_clients.values().index(chat_msg)])
                       sender.send('NL')
                       sender.send('{:02d}:{:02d} {} appointed as manager'.format(datetime.datetime.now().hour,
                                                                             datetime.datetime.now().minute,chat_msg))
                   else:
                       sender.send('NL')
                       sender.send(r"You can't appoint managers")
                   break
               elif (chat_cmd == '4'):
                   if(sender in chat_managers):
                       silent_clients.append(chat_clients.keys()[chat_clients.values().index(chat_msg)])
                       sender.send('NL')
                       sender.send('{:02d}:{:02d} {} has been muted'.format(datetime.datetime.now().hour,
                                                                             datetime.datetime.now().minute,chat_msg))
                   else:
                       sender.send('NL')
                       sender.send(r"You can't silence people!")
                   break
               if(client is sender):
                   client.send('NL')
               else:
                   if(chat_cmd=='1'):
                       client.send('{:02d}:{:02d} {}: {}'.format(datetime.datetime.now().hour,datetime.datetime.now().minute,nick,chat_msg))
                   elif(chat_cmd=='5'):
                       if(client is chat_clients.keys()[chat_clients.values().index(chat_msg)]):
                           client.send('{:02d}:{:02d} !{}: {}'.format(datetime.datetime.now().hour,datetime.datetime.now().minute,nick,p_msg))
       previous_sender=sender
       messages_to_send.remove(message)
while True:
    rlist,wlist,xlist=select.select([server_socket] + open_client_sockets,open_client_sockets,[])
    for current_socket in rlist:
        if(current_socket is server_socket):
            (new_socket,address)=server_socket.accept()
            open_client_sockets.append(new_socket)
            num+=1
            if(num==1):
                chat_managers.append(new_socket)
            chat_clients[new_socket] = 'Annonymus{0}'.format(num)

            chat_clients[new_socket]='Annonymus{0}'.format(num)
        else:
            try:
                msg=current_socket.recv(1024)
            except socket.error as e:
                if e.errno==10054:
                    msg=''
                else:
                    raise
            if(msg=='' or 'quit' in msg):
                if('quit' in msg):
                    messages_to_send.append((current_socket, 'quit'))
                    current_socket.send('quit')
                    open_client_sockets.remove(current_socket)

                else:
                    messages_to_send.append((current_socket, 'quit'))
                    try:
                        current_socket.send('quit')
                    except:
                        pass
                    open_client_sockets.remove(current_socket)

            else:
                messages_to_send.append((current_socket,msg))
    send_waiting_messages(wlist)
