import unicaja
import getpass
import sys

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Use: %s [dni]' % sys.argv[0]
        sys.exit(-1)

    password = getpass.getpass()
    session = unicaja.Unicaja(sys.argv[1], password)
    for account in session.accounts:
        print 'Balance: %s' % session.accounts[account]['balance']
        print 'Transactions:'
        for transaction in session.accounts[account]['transactions']:
            print '=> %s \t %s ' % (transaction[0], transaction[1])
