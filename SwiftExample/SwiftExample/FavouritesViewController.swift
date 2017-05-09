//
//  FavouritesViewController.swift
//  SwiftExample
//
//  Created by xavier green on 27/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import UIKit

class FavouritesViewController: UIViewController, UITableViewDelegate,UITableViewDataSource, UITextFieldDelegate {
    
    var all_questions = [String]()
    var favourites = Favourites()
    
    @IBOutlet var excep_amount: UITextField!
    
    @IBAction func retour(_ sender: Any) {
        dismiss(animated: true, completion: nil)
    }
    
    @IBOutlet var switchButton: UISwitch!
    
    @IBOutlet var favourite_questions_view: UITableView!
    
    func switchFav() {
        if switchButton.isOn {
            print("switching off")
            self.switchButton.setOn(false, animated: true)
            favourites.write_to_favourites(favourites_bool: "false")
        } else {
            print("switching on")
            self.switchButton.setOn(true, animated: true)
            favourites.write_to_favourites(favourites_bool: "true")
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        favourite_questions_view.delegate=self
        favourite_questions_view.dataSource=self
        excep_amount.delegate = self
        all_questions = favourites.read_file()
        excep_amount.text = favourites.read_file_transac()
        self.hideKeyboardWhenTappedAround()
        navigationController?.navigationBar.barTintColor = UIColor(colorLiteralRed: 87/255, green: 93/255, blue: 102/255, alpha: 1)
        navigationController?.navigationBar.tintColor = UIColor.white
        navigationController?.navigationBar.titleTextAttributes = [NSForegroundColorAttributeName: UIColor.white, NSFontAttributeName: UIFont.systemFont(ofSize: 22)]
//        self.switchButton.addTarget(self, action: #selector(self.switchFav), for: .touchUpInside)
        if !favourites.read_file_favourites() {
            self.switchButton.setOn(false, animated: false)
        }
        self.switchButton.addTarget(self, action: #selector(self.switchFav), for: .valueChanged)
    }
    
    func hideKeyboardWhenTappedAround() {
        let tap: UITapGestureRecognizer = UITapGestureRecognizer(target: self, action: #selector(self.dismissKeyboard))
        view.addGestureRecognizer(tap)
    }
    func dismissKeyboard() {
        view.endEditing(true)
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        self.view.endEditing(true)
        return false
    }
    
    func textFieldDidEndEditing(_ textField: UITextField) {
        let exceptional_amount = textField.text!
        favourites.write_to_file_transac(transaction_level: exceptional_amount)
    }
    
    func numberOfSections(in tableView: UITableView) -> Int {
        // #warning Incomplete implementation, return the number of sections
        return 1
    }
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.all_questions.count
    }
    internal func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let row = indexPath.row
        let cell = tableView.dequeueReusableCell(withIdentifier: "qCell",
                                                 for: indexPath) as! questionCell
        cell.question.text = self.all_questions[row]
        return cell
    }
    
    func tableView(_ tableView: UITableView, didHighlightRowAt indexPath: IndexPath) {
        let row = indexPath.row
        self.delete_popup(index: row)
    }
    
    func delete_popup(index: Int) {
        let alert = UIAlertController(title: "Supprimer des favoris", message: "Voulez vous supprimer la question {"+self.all_questions[index]+"} de vos favorits ?", preferredStyle: UIAlertControllerStyle.alert)
        alert.addAction(UIAlertAction(title: "Oui", style: UIAlertActionStyle.default, handler: {
            action in self.delete(index: index)
        }))
        alert.addAction(UIAlertAction(title: "Non", style: UIAlertActionStyle.cancel, handler: nil))
        self.present(alert, animated: true, completion: nil)
    }
    
    func delete(index: Int) {
        self.favourite_questions_view.beginUpdates()
        self.all_questions.remove(at: index)
        self.favourite_questions_view.deleteRows(at: [IndexPath(row: index, section: 0)], with: .automatic)
        self.favourite_questions_view.endUpdates()
        favourites.write_to_file(questions: self.all_questions)
    }

}

class questionCell: UITableViewCell {
    @IBOutlet weak var question: UILabel!
}
