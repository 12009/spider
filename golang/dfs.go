package main

import (
	"fmt"
	"github.com/urfave/cli"
	"os"
)

func tester() {
	fmt.Println("hello world !")
}

func main() {

	app := cli.NewApp()

	app.Flags = []cli.Flag{
		cli.StringFlag{
			Name:  "config, c",
			Value: "dfs.json",
			Usage: "the config file for Server and Client that the json format",
		},
		cli.StringFlag{
			Name:  "host, H",
			Value: "127.0.0.1",
			Usage: "the host that Server or Client connect",
		},
		cli.StringFlag{
			Name:  "port, P",
			Value: "8058",
			Usage: "the port that Server or Client listen",
		},
		cli.StringFlag{
			Name:  "up_dir, u",
			Value: "/data/dfs",
			Usage: "the upload dir for Server",
		},
		cli.StringFlag{
			Name:  "down_dir, d",
			Value: "/tmp/dfs",
			Usage: "the download dir for Client",
		},
	}

	app.EnableBashCompletion = true
	app.Commands = []cli.Command{
		{
			Name: "server",
			//Aliases: []string{"s"},
			Usage: "the DFS server!",
			Action: func(c *cli.Context) error {
				fmt.Println(c.Args().First())
				fmt.Println(c.Command.Names())
				tester()
				fmt.Println("complete")
				return nil
			},
		},
		{
			Name: "client",
			//Aliases: []string{"s"},
			Usage: "the DFS client!",
			Action: func(c *cli.Context) error {
				fmt.Println("add")
				return nil
			},
		},
	}

	//sort.Sort(cli.CommandsByName(app.Commands))

	app.Run(os.Args)
}
