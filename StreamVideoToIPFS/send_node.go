package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"time"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p-core/host"
	"github.com/libp2p/go-libp2p-core/peer"
	pubsub "github.com/libp2p/go-libp2p-pubsub"
	"github.com/libp2p/go-libp2p/p2p/discovery/mdns"
)

// DiscoveryInterval is how often we re-publish our mDNS records.
const DiscoveryInterval = time.Hour

// DiscoveryServiceTag is used in our mDNS advertisements to discover other chat peers.
const DiscoveryServiceTag = "p2p-video-streams"

// discoveryNotifee gets notified when we find a new peer via mDNS discovery
type discoveryNotifee struct {
	h host.Host
}

// HandlePeerFound connects to peers discovered via mDNS. Once they're connected,
// the PubSub system will automatically start interacting with them if they also
// support PubSub.
func (n *discoveryNotifee) HandlePeerFound(pi peer.AddrInfo) {
	fmt.Printf("discovered new peer %s\n", pi.ID.Pretty())
	err := n.h.Connect(context.Background(), pi)
	if err != nil {
		fmt.Printf("error connecting to peer %s: %s\n", pi.ID.Pretty(), err)
	}
}

const SockAddr = "./tmp/notify.sock"

func main() {
	// setup floodsub
	ctx := context.Background()
	h, err := libp2p.New(libp2p.ListenAddrStrings("/ip4/0.0.0.0/tcp/0"))
	if err != nil {
		panic(err)
	}
	ps, err := pubsub.NewFloodSub(ctx, h)
	if err != nil {
		panic(err)
	}

	// setup local mDNS discovery
	s := mdns.NewMdnsService(h, DiscoveryServiceTag, &discoveryNotifee{h: h})
	s.Start()

	// nick is universally unique identifier for this node (in prod, uses a public key)
	// nick is also tied to the topic that is broadcast for this stream
	// subscribers (stream viewers) can subscribe to this nick and receive updates
	// in this proof of concept, a node may only broadcast one video stream
	nick := "0"
	topic, err := ps.Join(nick)
	if err != nil {
		panic(err)
	}

	// read from domain socket
	if err := os.RemoveAll(SockAddr); err != nil {
		log.Fatal(err)
	}
	l, err := net.Listen("unix", SockAddr)
	defer os.RemoveAll(SockAddr)
	if err != nil {
		log.Fatal("listen error:", err)
	}
	defer l.Close()
	conn, err := l.Accept()
	defer conn.Close()
	if err != nil {
		log.Fatal("accept error:", err)
	}
	for {
		buf := make([]byte, 4096)
		n, err := conn.Read(buf)
		if err != nil || n == 0 {
			conn.Close()
			return
		}

		// publish notifications
		fmt.Println("send_node.go ", string(buf[:n]))
		topic.Publish(ctx, buf[:n])
	}
}
