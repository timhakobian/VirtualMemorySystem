// Timothy Hakobian ; ID#56197426
// Xean Nguyenla ; ID#17133321

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>

struct pageTableEntry{
    int vpn;
    int valid;
    int dirty;
    int pageNum;
};

struct pageAddresses{
    int available;
    int fifoPosition;
    int LRUvalue;
    int vpnInUse;
    int addresses[4];
    int values[4];
    int virtualAddresses[4];        //Only used for main mem
};

void makeSpace(struct pageTableEntry *pageTable, struct pageAddresses *mainMem, struct pageAddresses *disk, int virtualPageNum, char* replacementAlg, int fifoCounter, int fifoBound, int clock)
{


    if (strncmp(replacementAlg, "FIFO", 4) == 0)
    {
        int i = fifoBound;
        int brokenOut = 0;
        while(i < (fifoCounter + 1))
        {
            int mainMemIndex = 0;
            while(mainMemIndex < 4)
            {
                if (mainMem[mainMemIndex].fifoPosition == i)
                {
                    int valueIndex = 0;
                    while (valueIndex < 4)
                    {
                        disk[mainMem[mainMemIndex].vpnInUse].values[valueIndex] = mainMem[mainMemIndex].values[valueIndex];
                        valueIndex++;

                    }
                    pageTable[mainMem[mainMemIndex].vpnInUse].dirty = 0;
                    pageTable[mainMem[mainMemIndex].vpnInUse].pageNum = mainMem[mainMemIndex].vpnInUse;
                    pageTable[mainMem[mainMemIndex].vpnInUse].valid = 0;

                    mainMem[mainMemIndex].available = 1;
                    brokenOut = 1;
                    break;
                }
                mainMemIndex++;
            }

            if(brokenOut == 1)
            {
                break;
            }
            i++;
        }


    }

    else if (strncmp(replacementAlg, "LRU", 3) == 0)
    {
        int mainMemIndex = 0;
        int leastUsedValue = mainMem[0].LRUvalue;
        int victimPageIndex = 0;
        while(mainMemIndex < 4)
        {
            if (mainMem[mainMemIndex].LRUvalue < leastUsedValue)
            {
                leastUsedValue = mainMem[mainMemIndex].LRUvalue;
                victimPageIndex = mainMemIndex;
            }
            mainMemIndex++;
        }

        int valueIndex = 0;
        while (valueIndex < 4)
        {
            disk[mainMem[victimPageIndex].vpnInUse].values[valueIndex] = mainMem[victimPageIndex].values[valueIndex];
            valueIndex++;
        }


        mainMem[victimPageIndex].available = 1;
        pageTable[mainMem[victimPageIndex].vpnInUse].dirty = 0;
        pageTable[mainMem[victimPageIndex].vpnInUse].pageNum = mainMem[victimPageIndex].vpnInUse;
        pageTable[mainMem[victimPageIndex].vpnInUse].valid = 0;
    }
}

// returns the main mem page index
int copyPageTM(struct pageTableEntry *pageTable, struct pageAddresses *mainMem, struct pageAddresses *disk, int virtualPageNum)
{
    int successful = -1;
    int mainPageIndex = 0;
    while(mainPageIndex < 4)
    {
        if (mainMem[mainPageIndex].available == 1)
        {
            int addressI = 0;
            while(addressI < 4)
            {
                mainMem[mainPageIndex].values[addressI] = disk[virtualPageNum].values[addressI];
                mainMem[mainPageIndex].vpnInUse = virtualPageNum;
                mainMem[mainPageIndex].virtualAddresses[addressI] = disk[virtualPageNum].addresses[addressI];
                addressI++;
            }

            successful = mainPageIndex;
            mainMem[mainPageIndex].available = 0;
            pageTable[virtualPageNum].valid = 1;
            break;

        }
        mainPageIndex++;
    }

    return successful;
}

void readAddress(struct pageTableEntry **pageTable, struct pageAddresses **mainMem, struct pageAddresses **disk, int virtualPageNum, char* replacementAlg, int address, int *fifoCounter, int *fifoBound, int *clock)
{
    int mainMemIndex = 0;
    if ((*pageTable)[virtualPageNum].valid == 0)
    {
        printf("A Page Fault Has Occurred\n");

        mainMemIndex = copyPageTM(*pageTable, *mainMem, *disk, virtualPageNum);
        if (mainMemIndex == -1)
        {
            makeSpace(*pageTable, *mainMem, *disk, virtualPageNum, replacementAlg, *fifoCounter, *fifoBound, *clock);
            (*fifoBound)++;
            mainMemIndex = copyPageTM(*pageTable, *mainMem, *disk, virtualPageNum);
        }

        (*pageTable)[virtualPageNum].pageNum = mainMemIndex;
        (*mainMem)[mainMemIndex].fifoPosition = *fifoCounter;
        (*fifoCounter)++;



        int i = 0;
        while (i < 4)
        {

            if ((*mainMem)[mainMemIndex].virtualAddresses[i] == address)
            {
                printf("%d\n", (*mainMem)[mainMemIndex].values[i]);
                break;
            }

            i++;
        }

        (*mainMem)[mainMemIndex].LRUvalue = *clock;
    }

    else
    {
        while (mainMemIndex < 4)
        {
            int i = 0;
            int brokenOut = 0;
            while (i < 4)
            {
                if ((*mainMem)[mainMemIndex].virtualAddresses[i] == address)
                {
                    printf("%d\n", (*mainMem)[mainMemIndex].values[i]);
                    brokenOut = 1;
                    break;
                }

                i++;
            }

            if (brokenOut == 1)
            {
                (*mainMem)[mainMemIndex].LRUvalue = *clock;
                break;
            }
            mainMemIndex++;
        }
    }


}

void writeAddress(struct pageTableEntry **pageTable, struct pageAddresses **mainMem, struct pageAddresses** disk, int virtualPageNum, char* replacementAlg, int address, int value, int *fifoCounter, int *fifoBound, int *clock)
{
    int mainMemIndex = 0;
    if ((*pageTable)[virtualPageNum].valid == 0)
    {
        printf("A Page Fault Has Occurred\n");
        mainMemIndex = copyPageTM(*pageTable, *mainMem, *disk, virtualPageNum);
        if (mainMemIndex == -1)
        {
            makeSpace(*pageTable, *mainMem, *disk, virtualPageNum, replacementAlg, *fifoCounter, *fifoBound, *clock);
            (*fifoBound)++;
            mainMemIndex = copyPageTM(*pageTable, *mainMem, *disk, virtualPageNum);
        }

        (*pageTable)[virtualPageNum].pageNum = mainMemIndex;

        (*mainMem)[mainMemIndex].fifoPosition = *fifoCounter;
        (*fifoCounter)++;

        int i = 0;
        while(i < 4) {
            if ((*mainMem)[mainMemIndex].virtualAddresses[i] == address)
            {
                (*mainMem)[mainMemIndex].values[i] = value;
                break;
            }
            i++;
        }

        (*mainMem)[mainMemIndex].LRUvalue = *clock;
        (*pageTable)[virtualPageNum].dirty = 1;
    }

    else
    {
        while (mainMemIndex < 4)
        {
            int brokenOut = 0;
            int i = 0;
            while (i < 4)
            {
                if ((*mainMem)[mainMemIndex].virtualAddresses[i] == address)
                {
                    (*mainMem)[mainMemIndex].values[i] = value;
                    (*pageTable)[virtualPageNum].dirty = 1;
                    brokenOut = 1;
                    break;
                }
                i++;
            }

            if (brokenOut == 1)
            {
                (*mainMem)[mainMemIndex].LRUvalue = *clock;
                break;
            }

            mainMemIndex++;
        }

    }

}

void virtualMachine(char* replacementAlg)
{

    struct pageTableEntry*  pageTable = malloc(8 * (4 * sizeof(int*)));
    struct pageAddresses* mainMem = malloc(4 * (15 * sizeof(int*)));
    struct pageAddresses* disk = malloc(8 * (8 * sizeof(int*)));

    int fifoCounter = 0;
    int fifoBound = 0;
    int clock = 0;
    int i = 0;


    while (i < 32)
    {
        disk[i / 4].addresses[i % 4] = i;
        disk[i / 4].values[i % 4] = -1;
        i++;
    }

    i = 0;

    while (i < 16)
    {
        mainMem[i / 4].addresses[i % 4] = i;
        mainMem[i / 4].values[i % 4] = -1;
        mainMem[i / 4].available = 1;
        i++;
    }

    i = 0;

    while(i < 8)
    {
        pageTable[i].vpn = i;
        pageTable[i].valid = 0;
        pageTable[i].dirty = 0;
        pageTable[i].pageNum = i;
        i++;
    }

    char response[80];

    while(strncmp(response, "quit", 4) != 0)

    {

        printf("> ");
        fgets(response, 80, stdin);
        char* command = strtok(response, " ");
        char* address = strtok(NULL, " ");
        if (strncmp(command, "showptable", 10) == 0)
        {
            int i = 0;
            while(i < 8){
                printf("%d",pageTable[i].vpn);
                printf(":");
                printf("%d",pageTable[i].valid);
                printf(":");
                printf("%d",pageTable[i].dirty);
                printf(":");
                printf("%d\n",pageTable[i].pageNum);

                i++;
            }
        }

        if (strncmp(command, "read", 4) == 0)
        {
            int virtualPageNum = atoi(address) / 4;

            readAddress(&pageTable, &mainMem, &disk, virtualPageNum, replacementAlg, atoi(address), &fifoCounter, &fifoBound, &clock);
        }

        if (strncmp(command, "write", 5) == 0){
            char* value = strtok(NULL, " ");
            int virtualPageNum = atoi(address) / 4;

            writeAddress(&pageTable, &mainMem, &disk, virtualPageNum, replacementAlg, atoi(address), atoi(value), &fifoCounter, &fifoBound, &clock);

        }

        if (strncmp(command, "showmain", 8) == 0) {
            i = 0;
            while (i < 4){
                printf("%d:", mainMem[atoi(address)].addresses[i]);
                printf("%d\n", mainMem[atoi(address)].values[i]);
                i++;
            }
        }

        if (strncmp(command, "showdisk", 8) == 0)
        {
            i = 0;
            while (i < 4){
                printf("%d:", disk[atoi(address)].addresses[i]);
                printf("%d\n", disk[atoi(address)].values[i]);
                i++;
            }
        }

        clock++;
    }
}

int main(int argc, char* argv[])
{
    if (argc == 2)
        virtualMachine(argv[1]);
    else
        virtualMachine("FIFO");
    return 0;
}
