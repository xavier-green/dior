//
//  InitialViewController.swift
//  SwiftExample
//
//  Created by xavier green on 07/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import UIKit

@available(iOS 10.0, *)
class InitialViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        let chatView = ChatViewController()
        chatView.messages = makeNormalConversation()
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
