#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>

#define PORT 58000

int main(void){

    int fd, newfd;
    struct hostent *h;
    struct sockaddr_in serveraddr, clientaddr;
    char msg[80], buffer[80];
    int addrlen;


    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd == -1) {
        printf("ERROSOCKET\n"); 
        exit(1);
    }

    if((h=gethostbyname("douro")) == NULL){
        printf("ERROHOSTNAME\n"); 
        exit(1);
    }


    memset((void*)&serveraddr, (int)'\0', sizeof(serveraddr));
    serveraddr.sin_family = AF_INET;
    serveraddr.sin_addr.s_addr = ((struct in_addr *)(h->h_addr_list[0]))->s_addr;
    serveraddr.sin_port = htons((u_short)PORT);


    addrlen = sizeof(serveraddr);
    strncpy(msg, "test12345", 80);
    sendto(fd, msg, strlen(msg), 0, (struct sockaddr*)&serveraddr, addrlen);

    close(fd);
    return 0;
}
