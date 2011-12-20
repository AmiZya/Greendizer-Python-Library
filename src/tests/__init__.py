from greendizer import SellerClient
import greendizer.http


greendizer.http.API_ROOT = "http://api.local.greendizer.com/"


def main():
    seller = SellerClient(email="jimi.hendrix@greendizer.com",
                          password="password").seller
    print "Hello %s,\n" % seller.full_name
    invoices = seller.emails["jimi.hendrix@greendizer.com"].invoices.all
    invoices.populate()
    for invoice in invoices.resources:
        print invoice.total

    threads = seller.threads.search("read==False")
    threads.populate()
    for t in threads.resources:
        print t.snippet


if __name__ == "__main__":
    main()
