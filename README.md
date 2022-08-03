Simple chat api using TCP sockets

Features:
1. Each client has a permission level from NEW to ADMIN. Actions in API can be tagged by certain permission level to prevent users from executing commands they are not meant to
2. Modular structure: each Action is implemented using Reactable interface. This allows to define handlers for actions using classes which could be further split up into smaller methods.
3. Encryption: all messages are encrypted using Diffie-Hellman Elliptic Curve public key exchange

In the future I am planning on developing better modular structure as well as improve code readability and documentation. Now it operates as a server - client application, in the future I might do a truly p2p encrypted server with shared serverstate.
