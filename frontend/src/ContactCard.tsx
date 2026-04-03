import React from 'react';

interface ContactCardProps {
  contact: {
    id: string;
    name: string;
    mobile: string;
  };
  onDelete: (id: string) => void;
}

const ContactCard: React.FC<ContactCardProps> = ({ contact, onDelete }) => {
  return (
    <div>
      <h3>{contact.name}</h3>
      <p>Mobile: {contact.mobile}</p>
      <button onClick={() => onDelete(contact.id)}>Delete</button>
    </div>
  );
};

export default ContactCard;