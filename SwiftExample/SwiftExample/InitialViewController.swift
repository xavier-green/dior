//
//  InitialViewController.swift
//  SwiftExample
//
//  Created by xavier green on 07/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import UIKit
import JSQMessagesViewController

@available(iOS 10.0, *)
class InitialViewController: UIViewController {
    
    var favourites = Favourites()

    override func viewDidLoad() {
        super.viewDidLoad()
        let chatView = ChatViewController()
        let history = favourites.read_history()
        chatView.messages = history[0] as! [JSQMessage]
        let details = favourites.read_details()
        chatView.chat_details = details
        let chatNavigationController = UINavigationController(rootViewController: chatView)
        present(chatNavigationController, animated: true, completion: nil)
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
