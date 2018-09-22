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

int main(void) {

    int fd, newfd;
    struct hostent *h;
    struct sockaddr_in serveraddr, clientaddr;
    char msg[80], buffer[80];
    int addrlen;
    int nread;

    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd == -1) {
        printf("ERROSOCKET\n"); 
        exit(1);
    }

    memset((void*)&serveraddr, (int)'\0', sizeof(serveraddr));
    serveraddr.sin_family = AF_INET;
    serveraddr.sin_addr.s_addr = htonl(INADDR_ANY);
    //serveraddr.sin_addr.s_addr = ((struct in_addr *)(h->h_addr_list[0]))->s_addr;
    serveraddr.sin_port = htons((u_short)PORT);

    if ((bind(fd, (struct sockaddr*)&serveraddr, sizeof(serveraddr))) == -1){
        printf("ERROBIND\n");
        exit(1);
    }
    addrlen = sizeof(serveraddr);

    //sendto(fd, msg, strlen(msg), 0, (struct sockaddr*)&serveraddr, addrlen);
    nread = recvfrom(fd, buffer, sizeof(buffer), 0, (struct sockaddr*)&clientaddr, &addrlen);
    if (nread==-1) {
        printf("ERRORECV\n");
        exit(1);
    }
    else {
        printf("%s\n", buffer);
    }
    close(fd);
    return 0;
}
